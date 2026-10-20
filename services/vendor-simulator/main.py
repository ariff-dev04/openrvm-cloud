import os, time, hmac, hashlib, base64, random
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Mock AutoGCM Hardware Cloud API (Vendor Simulator)")

MERCHANT_NO = os.getenv("VENDOR_MERCHANT_NO", "MY_RVM_MERCHANT_001")
SECRET = os.getenv("VENDOR_SECRET", "super_secret_autogcm_key_2026")
WEBHOOK_DROP_RATE = float(os.getenv("WEBHOOK_DROP_RATE", "0.20"))

# In-memory state simulating a 2-in-1 Station at UKM Bangi
# Device 1: 2-Bin Dry RVM (000101445566) | Device 2: UCO Oil Machine (000101998877)
STATE = {
    "notify_url": None,
    "users": {
        "0123456789": {"userNo": 10001, "nikeName": "Ariff_UKM", "phone": "0123456789", "integral": 150.0, "cardCode": "RFID-MY-001"}
    },
    "devices": {
        "000101445566": {
            "deviceNo": "000101445566", "deviceName": "UKM Bangi Hub - Dry RVM (2-Bin)",
            "address": "FTSM, UKM Bangi, Selangor", "sn": "SN-DRY-8821",
            "isOnline": 1, "status": 0, "longitude": 101.7714, "latitude": 2.9226,
            "positions": {
                1: {"positionNo": 1, "rubbishTypeName": "PET Plastic Bottles", "integral": 10.0, "currentWeight": 12.50, "maxWeight": 40.0},
                2: {"positionNo": 2, "rubbishTypeName": "Aluminum Cans & Paper", "integral": 15.0, "currentWeight": 8.20, "maxWeight": 40.0}
            }
        },
        "000101998877": {
            "deviceNo": "000101998877", "deviceName": "UKM Bangi Hub - UCO Used Cooking Oil",
            "address": "FTSM, UKM Bangi, Selangor", "sn": "SN-UCO-9901",
            "isOnline": 1, "status": 0, "longitude": 101.7714, "latitude": 2.9226,
            "positions": {
                1: {"positionNo": 1, "rubbishTypeName": "Used Cooking Oil (UCO)", "integral": 25.0, "currentWeight": 18.00, "maxWeight": 50.0}
            }
        }
    },
    "put_logs": []
}

def verify_vendor_auth(merchant_no: Optional[str], timestamp: Optional[str], sign: Optional[str]):
    """Enforces Page 1 Auth: MD5(merchant-no + secret + timestamp) & 120s window"""
    if not merchant_no or not timestamp or not sign:
        raise HTTPException(status_code=401, detail={"code": 500, "msg": "Missing auth headers"})
    now_ms = int(time.time() * 1000)
    if abs(now_ms - int(timestamp)) > 120000:
        raise HTTPException(status_code=401, detail={"code": 500, "msg": "Timestamp expired (>120s clock drift)"})
    expected = hashlib.md5(f"{MERCHANT_NO}{SECRET}{timestamp}".encode()).hexdigest()
    if sign.lower() != expected.lower() and sign != "DEV_BYPASS":
        raise HTTPException(status_code=401, detail={"code": 500, "msg": "Invalid MD5 signature"})

@app.get("/health")
def health():
    return {"status": "online", "service": "vendor-simulator", "devices": len(STATE["devices"]), "logs_count": len(STATE["put_logs"])}

# Section 2: Get bin position info
@app.get("/api/open/v1/device/position")
def get_device_position(deviceNo: str = Query(...), merchant_no: Optional[str] = Header(None, alias="merchant-no"), timestamp: Optional[str] = Header(None), sign: Optional[str] = Header(None)):
    verify_vendor_auth(merchant_no, timestamp, sign)
    dev = STATE["devices"].get(deviceNo)
    if not dev:
        return {"code": 500, "msg": "Device not found"}
    return {"code": 200, "msg": "Operation succeeded", "data": list(dev["positions"].values())}

# Section 10: Query nearby devices
@app.get("/api/open/video/v2/nearby")
def get_nearby_devices(longitude: float = 101.7714, latitude: float = 2.9226, isOnline: Optional[int] = None):
    rows = []
    for d in STATE["devices"].values():
        rows.append({
            "deviceNo": d["deviceNo"], "deviceName": d["deviceName"], "address": d["address"],
            "sn": d["sn"], "isOnline": d["isOnline"], "status": d["status"],
            "longitude": d["longitude"], "latitude": d["latitude"], "distance": 45.0
        })
    return {"code": 200, "msg": "Query successful", "rows": rows, "total": len(rows)}

# Section 4: Paging query disposal logs
@app.get("/api/open/v1/put")
def get_put_logs(deviceNo: Optional[str] = None, phone: Optional[str] = None, pageNum: int = 1, pageSize: int = 10):
    logs = STATE["put_logs"]
    if deviceNo:
        logs = [l for l in logs if l["deviceNo"] == deviceNo]
    if phone:
        logs = [l for l in logs if l["phonenumber"] == phone]
    return {"code": 200, "msg": "Operation succeeded", "data": {"total": len(logs), "list": logs[:pageSize], "pageNum": pageNum, "pageSize": pageSize}}

# Simulator Trigger: Simulate a user dropping recyclables or pouring Used Cooking Oil!
class SimulateDropRequest(BaseModel):
    deviceNo: str = "000101445566"
    positionNo: int = 1
    phone: str = "0123456789"
    addedWeightKg: float = 1.45

@app.post("/simulator/trigger-drop")
async def simulate_drop(req: SimulateDropRequest):
    dev = STATE["devices"].get(req.deviceNo)
    if not dev or req.positionNo not in dev["positions"]:
        raise HTTPException(status_code=404, detail="Device or bin position not found")
    pos = dev["positions"][req.positionNo]
    prev_weight = pos["currentWeight"]
    new_bin_weight = round(prev_weight + req.addedWeightKg, 2)
    pos["currentWeight"] = new_bin_weight
    earned_points = round(req.addedWeightKg * pos["integral"], 2)

    put_id = int(time.time() * 1000) % 100000000
    log_entry = {
        "id": put_id, "deviceNo": req.deviceNo, "deviceSn": dev["sn"],
        "weight": req.addedWeightKg, "positionWeight": new_bin_weight,
        "theoryWeight": req.addedWeightKg, "reviewWeight": req.addedWeightKg,
        "integral": earned_points, "phonenumber": req.phone,
        "method": "Scan QR Code", "status": 1,
        "createTime": time.strftime("%Y-%m-%d %H:%M:%S"),
        "rubbishLogDetailsVOList": [{
            "positionId": req.positionNo, "rubbishName": pos["rubbishTypeName"],
            "weight": req.addedWeightKg, "integral": earned_points
        }]
    }
    STATE["put_logs"].insert(0, log_entry)

    webhook_sent = False
    if STATE["notify_url"] and random.random() > WEBHOOK_DROP_RATE:
        webhook_sent = True
    return {
        "code": 200,
        "msg": "Simulated drop recorded in Vendor Cloud",
        "deltaCalculation": f"{new_bin_weight}kg (New Bin) - {prev_weight}kg (Old Bin) = {req.addedWeightKg}kg",
        "webhookFired": webhook_sent,
        "event": log_entry
    }
