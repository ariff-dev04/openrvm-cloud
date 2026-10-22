from sqlalchemy import Column, Integer, String, Float, Boolean
from app.core.database import Base

class UserAccount(Base):
    __tablename__ = "users_v2"
    id = Column(Integer, primary_key=True, autoincrement=True)
    google_email = Column(String, nullable=True)
    phone = Column(String, unique=True, index=True)
    nickname = Column(String, default="Recycler")
    avatar_url = Column(String, default="https://api.dicebear.com/7.x/avataaars/svg?seed=Ariff")
    card_code = Column(String, default="RFID-MY-001")
    points_balance = Column(Float, default=0.0)    # Approved & Withdrawable Points
    pending_points = Column(Float, default=0.0)    # Waiting for Admin Verification
    total_recycled_kg = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=True)

class RecyclingSubmission(Base):
    __tablename__ = "submissions_v2"
    put_id = Column(Integer, primary_key=True)
    phone = Column(String, index=True)
    user_name = Column(String, default="Ariff Bin Zakaria")
    device_no = Column(String)
    station_name = Column(String)
    device_type = Column(String)                   # DRY_2BIN or UCO_OIL
    rubbish_type = Column(String)
    rate_per_kg = Column(Float, default=50.0)
    prev_bin_weight_kg = Column(Float, default=0.0)
    bin_position_weight_kg = Column(Float, default=0.0)
    submitted_weight_kg = Column(Float)
    verified_weight_kg = Column(Float, nullable=True)
    snapshot_urls = Column(String, nullable=True)  # "before_url,after_url" for Dry RVM; None for UCO
    points_awarded = Column(Float)
    audit_status = Column(String, default="PENDING") # PENDING, VERIFIED, REJECTED
    created_at = Column(String)

class WithdrawalRequest(Base):
    __tablename__ = "withdrawals_v2"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String, index=True)
    user_name = Column(String)
    amount_points = Column(Float)
    amount_rm = Column(Float)
    bank_name = Column(String)
    account_no = Column(String)
    account_holder_name = Column(String)
    status = Column(String, default="PENDING")     # PENDING, PAID, REJECTED
    created_at = Column(String)

class CleaningLog(Base):
    __tablename__ = "cleaning_logs_v2"
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_no = Column(String)
    station_name = Column(String)
    collector_name = Column(String)
    collected_weight_kg = Column(Float)
    cleaned_at = Column(String)

class AdminUser(Base):
    __tablename__ = "admin_users_v2"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String, default="OPERATOR")      # SUPER_ADMIN, OPERATOR, FINANCE
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(String)
