import os, time, hashlib, asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import redis
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- Environment Configuration ---
DB_USER = os.getenv("POSTGRES_USER", "openrvm_admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "rvm_local_prod_pass_99")
DB_NAME = os.getenv("POSTGRES_DB", "openrvm_db")
DB_HOST = os.getenv("DB_HOST", "postgres-db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")
SIMULATOR_URL = os.getenv("SIMULATOR_URL", "http://vendor-simulator:8081")
MERCHANT_NO = os.getenv("VENDOR_MERCHANT_NO", "MY_RVM_MERCHANT_001")
VENDOR_SECRET = os.getenv("VENDOR_SECRET", "super_secret_autogcm_key_2026")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
rdb = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# --- PostgreSQL Models ---
class UserAccount(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, index=True)
    nickname = Column(String)
    card_code = Column(String, nullable=True)
    points_balance = Column(Float, default=0.0)
    total_recycled_kg = Column(Float, default=0.0)

class StationDevice(Base):
    __tablename__ = "station_devices"
    device_no = Column(String, primary_key=True)
    station_name = Column(String)       # Unifies 2-in-1 RVM + UCO under 1 Station!
    device_type = Column(String)        # "DRY_2BIN" or "UCO_OIL"
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

class RecyclingSubmission(Base):
    __tablename__ = "recycling_submissions"
    put_id = Column(Integer, primary_key=True)
    phone = Column(String, index=True)
    device_no = Column(String)
    rubbish_type = Column(String)
    submitted_weight_kg = Column(Float)
    bin_position_weight_kg = Column(Float)
    points_awarded = Column(Float)
    audit_status = Column(String, default="PENDING") # PENDING, ACCEPTED, CORRECTED, REJECTED
    created_at = Column(String)

class WithdrawalRequest(Base):
    __tablename__ = "withdrawals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String)
    amount_points = Column(Float)
    amount_rm = Column(Float)
    bank_or_ewallet = Column(String)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime, server_default=func.now())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def vendor_headers() -> dict:
    """Generates Page 1 MD5 Signature: MD5(merchant-no + secret + timestamp)"""
    ts = str(int(time.time() * 1000))
    sign = hashlib.md5(f"{MERCHANT_NO}{VENDOR_SECRET}{ts}".encode()).hexdigest()
    return {"merchant-no": MERCHANT_NO, "timestamp": ts, "sign": sign}

async def sync_vendor_logs_once():
    """Polls Vendor API /api/open/v1/put and reconciles missing webhook transactions using Redis Idempotency"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{SIMULATOR_URL}/api/open/v1/put", headers=vendor_headers())
            data = resp.json()
            if data.get("code") != 200:
                return 0
            logs = data.get("data", {}).get("list", [])
            new_synced = 0
            with SessionLocal() as db:
                for item in logs:
                    put_id = item["id"]
                    # Redis Idempotency Check: Only process each put_id once!
                    if not rdb.setnx(f"processed_put:{put_id}", "1"):
                        continue
                    exists = db.query(RecyclingSubmission).filter_by(put_id=put_id).first()
                    if exists:
                        continue
                    details = item.get("rubbishLogDetailsVOList", [{}])[0]
                    sub = RecyclingSubmission(
                        put_id=put_id,
                        phone=item["phonenumber"],
                        device_no=item["deviceNo"],
                        rubbish_type=details.get("rubbishName", "Recyclables"),
                        submitted_weight_kg=item["weight"],
                        bin_position_weight_kg=item.get("positionWeight", item["weight"]),
                        points_awarded=item["integral"],
                        audit_status="PENDING",
                        created_at=item["createTime"]
                    )
                    db.add(sub)
                    user = db.query(UserAccount).filter_by(phone=item["phonenumber"]).first()
                    if not user:
                        user = UserAccount(phone=item["phonenumber"], nickname="Recycler", points_balance=0.0, total_recycled_kg=0.0)
                        db.add(user)
                    user.points_balance = round(user.points_balance + item["integral"], 2)
                    user.total_recycled_kg = round(user.total_recycled_kg + item["weight"], 2)
                    new_synced += 1
                db.commit()
            rdb.incr("metrics:sync_runs_total")
            return new_synced
    except Exception as e:
        print(f"[SyncWorker] Warning: {e}")
        return 0

async def background_poller():
    while True:
        await sync_vendor_logs_once()
        await asyncio.sleep(10) # Polls every 10 seconds to catch dropped vendor webhooks!

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(UserAccount).filter_by(phone="0123456789").first():
            db.add(UserAccount(phone="0123456789", nickname="Ariff_UKM", card_code="RFID-MY-001", points_balance=150.0, total_recycled_kg=12.5))
        if not db.query(StationDevice).first():
            db.add_all([
                StationDevice(device_no="000101445566", station_name="UKM Bangi 2-in-1 EcoHub", device_type="DRY_2BIN", address="FTSM, UKM Bangi, Selangor", latitude=2.9226, longitude=101.7714),
                StationDevice(device_no="000101998877", station_name="UKM Bangi 2-in-1 EcoHub", device_type="UCO_OIL", address="FTSM, UKM Bangi, Selangor", latitude=2.9226, longitude=101.7714)
            ])
        db.commit()
    task = asyncio.create_task(background_poller())
    yield
    task.cancel()

app = FastAPI(title="OpenRVM Core API & Reconciliation Engine", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    total_logs = db.query(RecyclingSubmission).count()
    return {"status": "healthy", "service": "openrvm-api", "synced_transactions": total_logs, "sync_worker_runs": int(rdb.get("metrics:sync_runs_total") or 0)}

@app.get("/api/stations")
async def get_unified_stations(db: Session = Depends(get_db)):
    """Returns 2-in-1 Unified Station data combining Dry 2-Bin RVM + UCO Oil Machine live bin levels"""
    devices = db.query(StationDevice).all()
    result = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for d in devices:
            resp = await client.get(f"{SIMULATOR_URL}/api/open/v1/device/position", params={"deviceNo": d.device_no}, headers=vendor_headers())
            bins = resp.json().get("data", []) if resp.status_code == 200 else []
            result.append({
                "deviceNo": d.device_no, "stationName": d.station_name, "deviceType": d.device_type,
                "address": d.address, "latitude": d.latitude, "longitude": d.longitude, "compartments": bins
            })
    return {"stationGroup": "UKM Bangi 2-in-1 EcoHub", "units": result}

@app.get("/api/user/{phone}/dashboard")
def get_user_dashboard(phone: str, db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter_by(phone=phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    logs = db.query(RecyclingSubmission).filter_by(phone=phone).order_by(RecyclingSubmission.put_id.desc()).all()
    withdrawals = db.query(WithdrawalRequest).filter_by(phone=phone).order_by(WithdrawalRequest.id.desc()).all()
    return {"user": user, "history": logs, "withdrawals": withdrawals}

class AuditAction(BaseModel):
    action: str # ACCEPTED, CORRECTED, REJECTED
    corrected_weight_kg: Optional[float] = None

@app.post("/api/admin/audit/{put_id}")
def audit_submission(put_id: int, req: AuditAction, db: Session = Depends(get_db)):
    sub = db.query(RecyclingSubmission).filter_by(put_id=put_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    user = db.query(UserAccount).filter_by(phone=sub.phone).first()
    if req.action == "REJECTED" and sub.audit_status != "REJECTED":
        if user:
            user.points_balance = round(max(0.0, user.points_balance - sub.points_awarded), 2)
        sub.points_awarded = 0.0
    elif req.action == "CORRECTED" and req.corrected_weight_kg is not None:
        rate = (sub.points_awarded / sub.submitted_weight_kg) if sub.submitted_weight_kg > 0 else 10.0
        new_pts = round(req.corrected_weight_kg * rate, 2)
        if user:
            user.points_balance = round(user.points_balance - sub.points_awarded + new_pts, 2)
        sub.submitted_weight_kg = req.corrected_weight_kg
        sub.points_awarded = new_pts
    sub.audit_status = req.action
    db.commit()
    return {"msg": f"Submission {put_id} updated to {req.action}", "submission": sub}

class SimulateTrigger(BaseModel):
    deviceNo: str = "000101445566"
    positionNo: int = 1
    phone: str = "0123456789"
    addedWeightKg: float = 1.25

@app.post("/api/simulator/drop")
async def trigger_simulated_drop(req: SimulateTrigger):
    """Allows the Vue 3 UI to trigger a live hardware drop and immediately syncs it!"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(f"{SIMULATOR_URL}/simulator/trigger-drop", json=req.model_dump())
        data = resp.json()
    await sync_vendor_logs_once()
    return data
