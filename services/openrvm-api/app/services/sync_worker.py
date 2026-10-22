import asyncio, time
import httpx
from app.core.config import settings
from app.core.database import SessionLocal, rdb
from app.core.security import generate_vendor_headers
from app.models.entities import UserAccount, RecyclingSubmission

async def sync_vendor_logs_once() -> int:
    """Polls Vendor API and places new submissions into PENDING escrow (users.pending_points)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.SIMULATOR_URL}/api/open/v1/put", headers=generate_vendor_headers())
            data = resp.json()
            if data.get("code") != 200:
                return 0
            logs = data.get("data", {}).get("list", [])
            new_synced = 0
            with SessionLocal() as db:
                for item in logs:
                    put_id = item["id"]
                    if not rdb.setnx(f"processed_put_v2:{put_id}", "1"):
                        continue
                    if db.query(RecyclingSubmission).filter_by(put_id=put_id).first():
                        continue

                    phone = item["phonenumber"]
                    user = db.query(UserAccount).filter_by(phone=phone).first()
                    if not user:
                        user = UserAccount(
                            phone=phone,
                            nickname="Ali Bin Abu",
                            points_balance=0.0,
                            pending_points=0.0,
                            total_recycled_kg=0.0
                        )
                        db.add(user)
                        db.flush()

                    sub = RecyclingSubmission(
                        put_id=put_id,
                        phone=phone,
                        user_name=user.nickname,
                        device_no=item["deviceNo"],
                        station_name=item.get("deviceName", "Eco Botanic Mall"),
                        device_type=item.get("deviceType", "DRY_2BIN"),
                        rubbish_type=item.get("rubbishName", "Plastic & Can"),
                        rate_per_kg=item.get("ratePerKg", 50.0),
                        prev_bin_weight_kg=item.get("prevWeight", 12.0),
                        bin_position_weight_kg=item.get("positionWeight", 13.25),
                        submitted_weight_kg=item["weight"],
                        verified_weight_kg=None,
                        snapshot_urls=item.get("putImgUrl"),
                        points_awarded=item["integral"],
                        audit_status="PENDING",
                        created_at=item["createTime"]
                    )
                    db.add(sub)
                    # Points go into PENDING escrow until Merchant Admin approves!
                    user.pending_points = round(user.pending_points + item["integral"], 2)
                    new_synced += 1
                db.commit()
            rdb.incr("metrics:sync_runs_v2")
            rdb.set("metrics:last_sync_time", time.strftime("%I:%M:%S %p"))
            return new_synced
    except Exception as e:
        print(f"[SyncWorker v2] Warning: {e}")
        return 0

async def background_poller():
    while True:
        await sync_vendor_logs_once()
        await asyncio.sleep(8)
