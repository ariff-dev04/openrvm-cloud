import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal, get_db, rdb
from app.models.entities import UserAccount, RecyclingSubmission, WithdrawalRequest, CleaningLog
from app.services.sync_worker import background_poller
from app.api import auth_routes, recycler_routes, admin_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(UserAccount).filter_by(phone="0123456789").first():
            db.add(UserAccount(
                phone="0123456789",
                google_email="ariff.ukm@gmail.com",
                nickname="Ariff Bin Zakaria",
                card_code="RFID-MY-001",
                points_balance=1500.0,
                pending_points=62.5,
                total_recycled_kg=12.5,
                is_verified=True
            ))
        if not db.query(RecyclingSubmission).first():
            b_img = "https://placehold.co/600x360/1e293b/f59e0b?text=BEFORE+(BIN+STATE)%0ABin+Weight:+14.15kg"
            a_img = "https://placehold.co/600x360/0f172a/10b981?text=AFTER+(SUBMISSION)%0A+1.25kg+Plastic+%26+Can"
            db.add_all([
                RecyclingSubmission(
                    put_id=129384, phone="0123456789", user_name="Ariff Bin Zakaria",
                    device_no="RVM-SK-001", station_name="Eco Botanic Mall", device_type="DRY_2BIN",
                    rubbish_type="Plastic & Can", rate_per_kg=50.0, prev_bin_weight_kg=14.15,
                    bin_position_weight_kg=15.40, submitted_weight_kg=1.25,
                    snapshot_urls=f"{b_img},{a_img}", points_awarded=62.5,
                    audit_status="PENDING", created_at="22/10/2026, 01:16:55 AM"
                ),
                RecyclingSubmission(
                    put_id=129350, phone="0123456789", user_name="Ariff Bin Zakaria",
                    device_no="UCO-SK-001", station_name="Eco Botanic Mall", device_type="UCO_OIL",
                    rubbish_type="Used Cooking Oil", rate_per_kg=80.0, prev_bin_weight_kg=40.50,
                    bin_position_weight_kg=42.50, submitted_weight_kg=2.00, verified_weight_kg=2.00,
                    snapshot_urls=None, points_awarded=160.0,
                    audit_status="VERIFIED", created_at="21/10/2026, 04:30:12 PM"
                )
            ])
        if not db.query(WithdrawalRequest).first():
            db.add(WithdrawalRequest(
                phone="0123456789", user_name="Ariff Bin Zakaria",
                amount_points=500.0, amount_rm=5.00, bank_name="Maybank",
                account_no="162012998877", account_holder_name="MUHAMMAD ARIFF BIN MOHD ZAKARIA",
                status="PENDING", created_at="22/10/2026, 10:15:00 AM"
            ))
        if not db.query(CleaningLog).first():
            db.add_all([
                CleaningLog(device_no="RVM-SK-001", station_name="Eco Botanic Mall", collector_name="Ahmad (South Team)", collected_weight_kg=38.5, cleaned_at="21/10/2026, 09:00:00 AM"),
                CleaningLog(device_no="UCO-SK-001", station_name="Eco Botanic Mall", collector_name="BioOil Logistics MY", collected_weight_kg=45.0, cleaned_at="20/10/2026, 06:15:00 PM")
            ])
        db.commit()
    task = asyncio.create_task(background_poller())
    yield
    task.cancel()

app = FastAPI(title="OpenRVM Cloud v2.0 Clean Layered API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_routes.router)
app.include_router(recycler_routes.router)
app.include_router(admin_routes.router)

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    return {
        "status": "healthy",
        "architecture": "Clean 3-Tier Layered v2.0",
        "synced_transactions": db.query(RecyclingSubmission).count(),
        "sync_worker_runs": int(rdb.get("metrics:sync_runs_v2") or 0)
    }
