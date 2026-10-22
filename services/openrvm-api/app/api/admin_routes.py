import os, time, hashlib
import httpx
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.core.database import get_db, rdb
from app.models.entities import UserAccount, RecyclingSubmission, WithdrawalRequest, CleaningLog, AdminUser
from app.schemas.dto import SubmissionAuditRequest, WithdrawalAuditRequest, AdminLoginRequest, AdminCreateRequest
from app.services.sync_worker import sync_vendor_logs_once

router = APIRouter(prefix="/api/admin", tags=["Merchant Admin Platform"])

MASTER_EMAIL = os.getenv("MASTER_ADMIN_EMAIL", "ariff.master@openrvm.my").strip().lower()
MASTER_PASS = os.getenv("MASTER_ADMIN_PASSWORD", "AriffDevOpsMaster2026!")

def hash_pw(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def require_write_access(x_admin_role: Optional[str] = Header(None)):
    """Blocks GUEST_AUDITOR (Public Recruiter Demo) from modifying database state!"""
    if x_admin_role == "GUEST_AUDITOR":
        raise HTTPException(
            status_code=403,
            detail="Read-Only Recruiter Demo Mode: Data modification is disabled for guest accounts. Sign in with Developer Master credentials to modify records."
        )

def ensure_seeded_admins(db: Session):
    # 1. Seed or sync Developer Master Admin from .env secrets
    master = db.query(AdminUser).filter_by(email=MASTER_EMAIL).first()
    if not master:
        db.add(AdminUser(
            email=MASTER_EMAIL,
            full_name="Ariff Zakaria (Developer Master)",
            role="SUPER_ADMIN",
            password_hash=hash_pw(MASTER_PASS),
            is_active=True,
            created_at=time.strftime("%d/%m/%Y")
        ))
    else:
        master.password_hash = hash_pw(MASTER_PASS)
        master.role = "SUPER_ADMIN"

    # 2. Seed Public Recruiter Read-Only Demo Account
    guest = db.query(AdminUser).filter_by(email="demo@openrvm.my").first()
    if not guest:
        db.add(AdminUser(
            email="demo@openrvm.my",
            full_name="Recruiter / Guest Viewer (Read-Only)",
            role="GUEST_AUDITOR",
            password_hash=hash_pw("demo123"),
            is_active=True,
            created_at=time.strftime("%d/%m/%Y")
        ))
    db.commit()

@router.post("/login")
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    ensure_seeded_admins(db)
    adm = db.query(AdminUser).filter_by(email=req.email.strip().lower()).first()
    if not adm or adm.password_hash != hash_pw(req.password):
        raise HTTPException(status_code=401, detail="Invalid Admin email or password")
    return {
        "token": f"adm-jwt-{adm.id}-{int(time.time())}",
        "admin": {"id": adm.id, "email": adm.email, "full_name": adm.full_name, "role": adm.role}
    }

@router.get("/accounts")
def list_admin_accounts(db: Session = Depends(get_db)):
    ensure_seeded_admins(db)
    return db.query(AdminUser).order_by(AdminUser.id.asc()).all()

@router.post("/accounts", dependencies=[Depends(require_write_access)])
def create_admin_account(req: AdminCreateRequest, db: Session = Depends(get_db)):
    email_clean = req.email.strip().lower()
    if db.query(AdminUser).filter_by(email=email_clean).first():
        raise HTTPException(status_code=400, detail="Admin email already exists")
    new_adm = AdminUser(
        email=email_clean,
        full_name=req.full_name,
        role=req.role,
        password_hash=hash_pw(req.password),
        is_active=True,
        created_at=time.strftime("%d/%m/%Y")
    )
    db.add(new_adm)
    db.commit()
    return {"msg": f"Created {req.role} account for {req.full_name}"}

@router.delete("/accounts/{admin_id}", dependencies=[Depends(require_write_access)])
def delete_admin_account(admin_id: int, db: Session = Depends(get_db)):
    adm = db.query(AdminUser).filter_by(id=admin_id).first()
    if not adm or adm.role in ("SUPER_ADMIN", "GUEST_AUDITOR"):
        raise HTTPException(status_code=400, detail="Cannot delete protected system accounts")
    db.delete(adm)
    db.commit()
    return {"msg": "Staff account removed"}

@router.get("/overview")
async def get_admin_overview(db: Session = Depends(get_db)):
    pending_withdrawals = db.query(WithdrawalRequest).filter_by(status="PENDING").count()
    total_points = db.query(func.coalesce(func.sum(UserAccount.points_balance), 0.0)).scalar()
    total_weight = db.query(func.coalesce(func.sum(UserAccount.total_recycled_kg), 0.0)).scalar()

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"{settings.SIMULATOR_URL}/api/open/v1/devices")
        devices = resp.json().get("data", []) if resp.status_code == 200 else []
    online_machines = sum(1 for d in devices if d.get("isOnline") == 1 and not d.get("maintenanceMode"))

    submissions = db.query(RecyclingSubmission).order_by(RecyclingSubmission.put_id.desc()).all()
    withdrawals = db.query(WithdrawalRequest).order_by(WithdrawalRequest.id.desc()).all()
    cleaning_logs = db.query(CleaningLog).order_by(CleaningLog.id.desc()).all()
    users = db.query(UserAccount).order_by(UserAccount.id.desc()).all()

    return {
        "kpis": {
            "pendingWithdrawals": pending_withdrawals,
            "onlineMachines": f"{online_machines} / {len(devices)}",
            "totalPoints": round(float(total_points), 2),
            "recycledWeightKg": round(float(total_weight), 2),
            "lastSynced": rdb.get("metrics:last_sync_time") or "Just now",
            "syncRuns": int(rdb.get("metrics:sync_runs_v2") or 0)
        },
        "submissions": submissions,
        "withdrawals": withdrawals,
        "cleaningLogs": cleaning_logs,
        "machines": devices,
        "users": users
    }

@router.post("/submissions/force-sync")
async def force_sync():
    synced = await sync_vendor_logs_once()
    return {"msg": f"Force Sync completed ({synced} new hardware records pulled)"}

@router.post("/submissions/{put_id}/audit", dependencies=[Depends(require_write_access)])
def audit_submission(put_id: int, req: SubmissionAuditRequest, db: Session = Depends(get_db)):
    sub = db.query(RecyclingSubmission).filter_by(put_id=put_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    user = db.query(UserAccount).filter_by(phone=sub.phone).first()
    old_pts = sub.points_awarded

    if req.action in ("VERIFIED", "CORRECTED"):
        actual_w = req.actual_weight_kg if (req.action == "CORRECTED" and req.actual_weight_kg is not None) else sub.submitted_weight_kg
        new_pts = round(actual_w * sub.rate_per_kg, 2)
        if user and sub.audit_status == "PENDING":
            user.pending_points = round(max(0.0, user.pending_points - old_pts), 2)
            user.points_balance = round(user.points_balance + new_pts, 2)
            user.total_recycled_kg = round(user.total_recycled_kg + actual_w, 2)
        sub.verified_weight_kg = actual_w
        sub.points_awarded = new_pts
        sub.audit_status = "VERIFIED"
    elif req.action == "REJECTED":
        if user and sub.audit_status == "PENDING":
            user.pending_points = round(max(0.0, user.pending_points - old_pts), 2)
        sub.points_awarded = 0.0
        sub.audit_status = "REJECTED"

    db.commit()
    return {"msg": f"Submission #{put_id} marked as {sub.audit_status}", "submission": sub}

@router.post("/withdrawals/{withdrawal_id}/audit", dependencies=[Depends(require_write_access)])
def audit_withdrawal(withdrawal_id: int, req: WithdrawalAuditRequest, db: Session = Depends(get_db)):
    w = db.query(WithdrawalRequest).filter_by(id=withdrawal_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Withdrawal request not found")
    if w.status != "PENDING":
        raise HTTPException(status_code=400, detail="Withdrawal already processed")

    if req.action == "REJECTED":
        user = db.query(UserAccount).filter_by(phone=w.phone).first()
        if user:
            user.points_balance = round(user.points_balance + w.amount_points, 2)
        w.status = "REJECTED"
    else:
        w.status = "PAID"

    db.commit()
    return {"msg": f"Withdrawal #{withdrawal_id} updated to {w.status}", "withdrawal": w}

@router.post("/machines/{device_no}/toggle-maintenance", dependencies=[Depends(require_write_access)])
async def toggle_machine_maintenance(device_no: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(f"{settings.SIMULATOR_URL}/api/open/v1/device/{device_no}/toggle-maintenance")
        return resp.json()
