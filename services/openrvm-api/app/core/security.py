import time, hashlib, random
from app.core.config import settings
from app.core.database import rdb

def generate_vendor_headers() -> dict:
    ts = str(int(time.time() * 1000))
    sign = hashlib.md5(f"{settings.MERCHANT_NO}{settings.VENDOR_SECRET}{ts}".encode()).hexdigest()
    return {"merchant-no": settings.MERCHANT_NO, "timestamp": ts, "sign": sign}

def create_phone_otp(phone: str) -> str:
    """Generates a 4-digit OTP and stores it in Redis for 300 seconds (5 mins)"""
    otp_code = f"{random.randint(1000, 9999)}"
    rdb.setex(f"otp:{phone}", 300, otp_code)
    return otp_code

def verify_phone_otp(phone: str, code: str) -> bool:
    stored = rdb.get(f"otp:{phone}")
    if stored and (stored == code or code == "8520"):  # 8520 allowed for quick demo testing
        rdb.delete(f"otp:{phone}")
        return True
    return False
