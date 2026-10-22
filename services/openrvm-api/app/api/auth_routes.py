from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_phone_otp, verify_phone_otp
from app.models.entities import UserAccount, RecyclingSubmission, WithdrawalRequest
from app.schemas.dto import SendOtpRequest, VerifyOtpRequest

router = APIRouter(prefix="/api/auth", tags=["Authentication & PDPA"])

from app.schemas.dto import GoogleLoginRequest

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
    otp = create_phone_otp(req.phone)
    user = db.query(UserAccount).filter_by(phone=req.phone).first()
    if not user:
        user = UserAccount(
            phone=req.phone,
            nickname=req.nickname or "Recycler",
            google_email=req.email,
            points_balance=0.0,
            pending_points=0.0,
            total_recycled_kg=0.0,
            is_verified=False
        )
        db.add(user)
        db.commit()
    # Returns demo_otp in response so testers/recruiters can see the 4-digit code without paid SMS!
    return {"msg": "4-digit OTP generated in Redis (TTL 300s)", "phone": req.phone, "demo_otp": otp}

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
