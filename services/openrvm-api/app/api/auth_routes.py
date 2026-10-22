from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_phone_otp, verify_phone_otp
from app.models.entities import UserAccount, RecyclingSubmission, WithdrawalRequest
from app.schemas.dto import GoogleLoginRequest, SendOtpRequest, VerifyOtpRequest

router = APIRouter(prefix="/api/auth", tags=["Authentication & PDPA"])

def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return "another account"
    name, domain = email.split("@", 1)
    return f"{name[:2]}***@{domain}"

@router.post("/google-check")
def check_google_account(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Checks if a Google Email is already bound & OTP-verified so returning users sign in directly!"""
    email_clean = req.email.strip().lower()
    user = db.query(UserAccount).filter(UserAccount.google_email.ilike(email_clean)).first()
    if user and user.is_verified and user.phone:
        return {
            "status": "EXISTING_VERIFIED",
            "msg": f"Welcome back, {user.nickname}!",
            "user": user
        }
    return {
        "status": "NEW_USER",
        "email": email_clean,
        "nickname": req.nickname
    }

@router.post("/send-otp")
def send_otp(req: SendOtpRequest, db: Session = Depends(get_db)):
    clean_phone = req.phone.strip()
    clean_email = (req.email or "").strip().lower()

    # 1. Check if this phone number is already bound to a DIFFERENT Google email!
    existing_by_phone = db.query(UserAccount).filter_by(phone=clean_phone).first()
    if existing_by_phone and existing_by_phone.google_email:
        if existing_by_phone.google_email.strip().lower() != clean_email:
            raise HTTPException(
                status_code=409,
                detail=f"Phone +60{clean_phone} is already bound to {mask_email(existing_by_phone.google_email)}. Please sign in with that Google account instead."
            )

    # 2. Check if this Google email is already bound to a DIFFERENT phone number!
    if clean_email:
        existing_by_email = db.query(UserAccount).filter(UserAccount.google_email.ilike(clean_email)).first()
        if existing_by_email and existing_by_email.phone != clean_phone:
            raise HTTPException(
                status_code=409,
                detail=f"Email {clean_email} is already bound to phone +60{existing_by_email.phone}."
            )

    otp = create_phone_otp(clean_phone)
    if not existing_by_phone:
        user = UserAccount(
            phone=clean_phone,
            nickname=req.nickname or "Recycler",
            google_email=clean_email,
            points_balance=0.0,
            pending_points=0.0,
            total_recycled_kg=0.0,
            is_verified=False
        )
        db.add(user)
    else:
        existing_by_phone.google_email = clean_email or existing_by_phone.google_email
        existing_by_phone.nickname = req.nickname or existing_by_phone.nickname
    db.commit()

    return {"msg": "4-digit OTP generated in Redis (TTL 300s)", "phone": clean_phone, "demo_otp": otp}

@router.post("/verify-otp")
def verify_otp(req: VerifyOtpRequest, db: Session = Depends(get_db)):
    if not verify_phone_otp(req.phone, req.code):
        raise HTTPException(status_code=400, detail="Invalid or expired 4-digit OTP code")
    user = db.query(UserAccount).filter_by(phone=req.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return {"msg": "Success! Phone bound to RVM hardware account.", "user": user}

@router.delete("/account/{phone}")
def delete_user_account(phone: str, db: Session = Depends(get_db)):
    """PDPA Compliance: Purges user profile, submissions, and withdrawal records"""
    user = db.query(UserAccount).filter_by(phone=phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(RecyclingSubmission).filter_by(phone=phone).delete()
    db.query(WithdrawalRequest).filter_by(phone=phone).delete()
    db.delete(user)
    db.commit()
    return {"msg": f"Account {phone} and all personal data permanently deleted."}
