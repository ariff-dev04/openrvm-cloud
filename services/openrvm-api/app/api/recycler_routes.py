import time
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.entities import UserAccount, RecyclingSubmission, WithdrawalRequest
from app.schemas.dto import SimulateDropPayload, WithdrawalCreateRequest
from app.services.sync_worker import sync_vendor_logs_once

router = APIRouter(prefix="/api", tags=["Recycler User App"])

@router.get("/stations")
async def get_stations():
    """Groups 2-in-1 devices (e.g. RVM-SK-001 + UCO-SK-001 at Eco Botanic Mall) into unified Station cards"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"{settings.SIMULATOR_URL}/api/open/v1/devices")
        devices = resp.json().get("data", []) if resp.status_code == 200 else []

    grouped = {}
    for d in devices:
        name = d["deviceName"]
        if name not in grouped:
            grouped[name] = {
                "stationName": name,
                "zone": d.get("zone", "South Area"),
                "address": d["address"],
                "latitude": d.get("latitude", 1.4402),
                "longitude": d.get("longitude", 103.6180),
                "distanceKm": d.get("distance", 1.2),
                "supportPhone": d.get("supportPhone", "+60 12-345 6789"),
                "isOnline": d["isOnline"] == 1 and not d.get("maintenanceMode", False),
                "bins": [],
                "devices": []
            }

        grouped[name]["devices"].append(d)
        for pos in d["positions"].values():
            pct = round((pos["currentWeight"] / pos["maxWeight"]) * 100)
            grouped[name]["bins"].append({
                "deviceNo": d["deviceNo"],
                "deviceType": d["deviceType"],
                "positionNo": pos["positionNo"],
                "rubbishTypeName": pos["rubbishTypeName"],
                "ratePerKg": pos["integral"],
                "currentWeight": pos["currentWeight"],
                "maxWeight": pos["maxWeight"],
                "fillPercent": min(100, pct),
                "statusLabel": "FULL" if pct >= 95 else ("ALMOST FULL" if pct >= 80 else "NORMAL")
            })
    return {"stations": list(grouped.values()), "rawDevices": devices}

@router.get("/user/{phone}/dashboard")
def get_user_dashboard(phone: str, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter_by(phone=phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found or has been deleted")
    history = db.query(RecyclingSubmission).filter_by(phone=phone).order_by(RecyclingSubmission.put_id.desc()).all()
    withdrawals = db.query(WithdrawalRequest).filter_by(phone=phone).order_by(WithdrawalRequest.id.desc()).all()
    return {"user": user, "history": history, "withdrawals": withdrawals}

@router.post("/simulator/drop")
async def trigger_drop(req: SimulateDropPayload):
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(f"{settings.SIMULATOR_URL}/simulator/trigger-drop", json=req.model_dump())
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail", "Drop failed"))
        data = resp.json()
    await sync_vendor_logs_once()
    return data

@router.post("/user/withdraw")
def request_withdrawal(req: WithdrawalCreateRequest, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter_by(phone=req.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    rm_val = round(req.amount_points / 100.0, 2)  # 100 pts = RM 1.00 (1500 pts = RM 15.00)
    if rm_val < 5.0 or rm_val > 200.0:
        raise HTTPException(status_code=400, detail="Withdrawal must be between RM 5.00 (500 pts) and RM 200.00 (20,000 pts)")
    if user.points_balance < req.amount_points:
        raise HTTPException(status_code=400, detail="Insufficient approved points balance")

    user.points_balance = round(user.points_balance - req.amount_points, 2)
    w = WithdrawalRequest(
        phone=req.phone,
        user_name=user.nickname,
        amount_points=req.amount_points,
        amount_rm=rm_val,
        bank_name=req.bank_name,
        account_no=req.account_no,
        account_holder_name=req.account_holder_name,
        status="PENDING",
        created_at=time.strftime("%d/%m/%Y, %I:%M:%S %p")
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return {"msg": "Withdrawal request submitted for Merchant Admin approval", "withdrawal": w, "user": user}
