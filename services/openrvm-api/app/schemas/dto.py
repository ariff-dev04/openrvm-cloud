from pydantic import BaseModel
from typing import Optional

class GoogleLoginRequest(BaseModel):
    email: str = "ariff.ukm@gmail.com"
    nickname: str = "Ariff Bin Zakaria"

class SendOtpRequest(BaseModel):
    phone: str
    nickname: Optional[str] = "Ariff Bin Zakaria"
    email: Optional[str] = "ariff.ukm@gmail.com"

class VerifyOtpRequest(BaseModel):
    phone: str
    code: str

class SimulateDropPayload(BaseModel):
    deviceNo: str = "RVM-SK-001"
    positionNo: int = 1
    phone: str = "0123456789"
    addedWeightKg: float = 1.25

class WithdrawalCreateRequest(BaseModel):
    phone: str
    amount_points: float
    bank_name: str
    account_no: str
    account_holder_name: str

class SubmissionAuditRequest(BaseModel):
    action: str  # VERIFIED, CORRECTED, REJECTED
    actual_weight_kg: Optional[float] = None

class WithdrawalAuditRequest(BaseModel):
    action: str  # PAID, REJECTED

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class AdminCreateRequest(BaseModel):
    email: str
    full_name: str
    role: str = "OPERATOR"
    password: str
