import os, time, hashlib, random
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Mock AutoGCM Hardware Cloud API v2.0")

MERCHANT_NO = os.getenv("VENDOR_MERCHANT_NO", "MY_RVM_MERCHANT_001")
SECRET = os.getenv("VENDOR_SECRET", "super_secret_autogcm_key_2026")

# Realistic SVG Data-URI Snapshots for "BEFORE (BIN STATE)" and "AFTER (SUBMISSION)"
BEFORE_SNAPSHOT = "https://placehold.co/600x360/1e293b/f59e0b?text=BEFORE+(BIN+STATE)%0ACamera+Snapshot+12.5kg"
AFTER_SNAPSHOT = "https://placehold.co/600x360/0f172a/38bdf8?text=AFTER+(SUBMISSION)%0APET+Bottles+Detected"

STATE = {
    "devices": {
        "RVM-SK-001": {
            "deviceNo": "RVM-SK-001", "deviceName": "Eco Botanic Mall", "zone": "South Area",
            "address": "L1-04, Eco Galleria, Iskandar Puteri", "sn": "SN-SK-001",
            "deviceType": "DRY_2BIN", "isOnline": 1, "status": 0, "maintenanceMode": False,
            "longitude": 103.6180, "latitude": 1.4402, "distance": 1.2, "supportPhone": "+60 12-345 6789",
            "positions": {
                1: {"positionNo": 1, "rubbishTypeName": "Plastic & Can", "integral": 50.0, "currentWeight": 18.0, "maxWeight": 40.0}
            }
        },
        "UCO-SK-001": {
            "deviceNo": "UCO-SK-001", "deviceName": "Eco Botanic Mall", "zone": "South Area",
            "address": "L1-04, Eco Galleria, Iskandar Puteri", "sn": "SN-UCO-001",
            "deviceType": "UCO_OIL", "isOnline": 1, "status": 0, "maintenanceMode": False,
            "longitude": 103.6180, "latitude": 1.4402, "distance": 1.2, "supportPhone": "+60 12-345 6789",
            "positions": {
                1: {"positionNo": 1, "rubbishTypeName": "Used Cooking Oil", "integral": 80.0, "currentWeight": 42.5, "maxWeight": 50.0}
            }
        },
        "RVM-JB-002": {
            "deviceNo": "RVM-JB-002", "deviceName": "JB City Square", "zone": "South Area",
            "address": "B1-12, Jalan Wong Ah Fook, JB", "sn": "SN-JB-002",
            "deviceType": "DRY_2BIN", "isOnline": 1, "status": 1, "maintenanceMode": False,
            "longitude": 103.7635, "latitude": 1.4614, "distance": 3.5, "supportPhone": "+60 12-345 6789",
            "positions": {
                1: {"positionNo": 1, "rubbishTypeName": "Plastic & Can", "integral": 50.0, "currentWeight": 40.0, "maxWeight": 40.0},
                2: {"positionNo": 2, "rubbishTypeName": "Paper", "integral": 30.0, "currentWeight": 8.0, "maxWeight": 40.0}
            }
        },
        "RVM-PJ-003": {
            "deviceNo": "RVM-PJ-003", "deviceName": "Paradigm Mall", "zone": "Central Area",
            "address": "LG-09, Kelana Jaya, Selangor", "sn": "SN-PJ-003",
            "deviceType": "DRY_2BIN", "isOnline": 0, "status": 2, "maintenanceMode": True,
            "longitude": 101.5960, "latitude": 3.1048, "distance": 5.8, "supportPhone": "+60 17-889 1122",
            "positions": {
                1: {"positionNo": 1, "rubbishTypeName": "Plastic & Can", "integral": 50.0, "currentWeight": 10.2, "maxWeight": 40.0},
                2: {"positionNo": 2, "rubbishTypeName": "Paper", "integral": 30.0, "currentWeight": 14.5, "maxWeight": 40.0}
            }
        }
    },
    "put_logs": []
}

@app.get("/health")
def health():
    return {"status": "online", "devices": len(STATE["devices"]), "logs_count": len(STATE["put_logs"])}

@app.get("/api/open/v1/devices")
def get_all_devices():
    return {"code": 200, "data": list(STATE["devices"].values())}

@app.post("/api/open/v1/device/{device_no}/toggle-maintenance")
def toggle_maintenance(device_no: str):
    dev = STATE["devices"].get(device_no)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    dev["maintenanceMode"] = not dev["maintenanceMode"]
    dev["isOnline"] = 0 if dev["maintenanceMode"] else 1
    dev["status"] = 2 if dev["maintenanceMode"] else 0
    return {"code": 200, "device": dev}

@app.get("/api/open/v1/put")
def get_put_logs():
    return {"code": 200, "data": {"total": len(STATE["put_logs"]), "list": STATE["put_logs"]}}

class SimulateDropRequest(BaseModel):
    deviceNo: str = "RVM-SK-001"
    positionNo: int = 1
    phone: str = "0123456789"
    addedWeightKg: float = 1.25

@app.post("/simulator/trigger-drop")
def simulate_drop(req: SimulateDropRequest):
    dev = STATE["devices"].get(req.deviceNo)
    if not dev or req.positionNo not in dev["positions"]:
        raise HTTPException(status_code=404, detail="Device or bin position not found")
    if dev["maintenanceMode"]:
        raise HTTPException(status_code=400, detail="Machine is currently in MAINTENANCE mode")

    pos = dev["positions"][req.positionNo]
    prev_weight = pos["currentWeight"]
    new_weight = round(prev_weight + req.addedWeightKg, 2)
    pos["currentWeight"] = new_weight
    points = round(req.addedWeightKg * pos["integral"], 2)
    put_id = int(time.time() * 1000) % 100000000

    # Dry RVM captures Before & After snapshot URLs separated by a comma; UCO has None
    snapshot_str = None
    if dev["deviceType"] == "DRY_2BIN":
        b_url = f"https://placehold.co/600x360/1e293b/f59e0b?text=BEFORE+(BIN+STATE)%0ABin+Weight:+{prev_weight}kg"
        a_url = f"https://placehold.co/600x360/0f172a/10b981?text=AFTER+(SUBMISSION)%0A+{req.addedWeightKg}kg+{pos['rubbishTypeName'].replace(' ', '+')}"
        snapshot_str = f"{b_url},{a_url}"

    log_entry = {
        "id": put_id,
        "deviceNo": req.deviceNo,
        "deviceName": dev["deviceName"],
        "deviceType": dev["deviceType"],
        "positionNo": req.positionNo,
        "rubbishName": pos["rubbishTypeName"],
        "ratePerKg": pos["integral"],
        "prevWeight": prev_weight,
        "positionWeight": new_weight,
        "weight": req.addedWeightKg,
        "integral": points,
        "phonenumber": req.phone,
        "putImgUrl": snapshot_str,
        "createTime": time.strftime("%d/%m/%Y, %I:%M:%S %p")
    }
    STATE["put_logs"].insert(0, log_entry)
    return {"code": 200, "msg": "Drop recorded (Pending Admin Approval)", "event": log_entry}
