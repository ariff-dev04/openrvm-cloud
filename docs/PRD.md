# OpenRVM v2.0 — Product Requirements Document (PRD)

## 1. Authentication & Hardware Phone Binding Flow
1. **Welcome (`/welcome`) -> Google Sign-In (`/login`):** User signs in via Google OAuth2 (or Demo Login).
2. **Phone OTP Verification (`/verify-phone` -> `/verify-otp`):**
   - Because the physical RVM/UCO hardware API identifies recyclers by `phone`, users enter their Malaysian phone number (`+60...`).
   - Backend generates a 4-digit OTP stored in Redis (`otp:{phone}`, TTL 300s).
   - Once confirmed, user reaches `/auth-success` and is routed to Homepage (`/`).

## 2. Delayed Point Approval & Camera Snapshot Verification Workflow
1. **Dry 2-Bin RVM (`DRY_2BIN`):**
   - Hardware captures a concatenated **Before & After Camera Snapshot URL string** (`snapshot_urls = "before_url,after_url"`) alongside `prev_bin_weight_kg`, `new_bin_weight_kg`, and `submitted_weight_kg`.
2. **Used Cooking Oil Machine (`UCO_OIL`):**
   - Built-in fluid sensor prevents water/impurity fraud automatically; `snapshot_urls` is `null` and only weight telemetry is sent.
3. **Pending Points Escrow:**
   - All new recycling drops start as `audit_status = "PENDING"`.
   - Points are added to `users.pending_points` (displayed as `+{pending_points} pending` on the User Homepage).
   - Points are **NOT** added to withdrawable `users.points_balance` until the Merchant Admin inspects the Before/After photos (for Dry RVM) or UCO weight in `admin.rvm.ariff.lab` and clicks **Approve** (or **Correct**).

## 3. Point Withdrawal & Manual Bank Payout Flow
1. User navigates to `/withdraw` from the Homepage Points Card.
2. Enters `amount_points` (Min RM 5.00 / Max RM 200.00), selects `bank_name`, inputs `account_no`, and enters `account_holder_name` (Full Name per IC).
3. Submitting deducts `amount_points` from `users.points_balance` and creates a `PENDING` record in `withdrawals`.
4. Merchant Admin reviews the bank details in `admin.rvm.ariff.lab`, executes the manual bank transfer, and marks the withdrawal `APPROVED` (or `REJECTED`, which refunds the points).

## 4. PDPA Account & Data Deletion
- Users can click **Delete My Account & Data** on `/profile` to cascade-delete their profile, submissions, and withdrawal records after testing.

## 5. Merchant Admin Platform (`admin.rvm.ariff.lab`) Specification

### 5.1 Sidebar & Multi-Tab Workspace
- **Sidebar Sections:** `Dashboard`, `Submissions`, `Withdrawals`, `Users`, `Machines`, `Waste Logs`, `Admin Access`, `Settings`, `Logout`.
- **Top Workspace Tabs:** Supports switching between open modules (`Dashboard`, `Submissions`, `Withdrawals`, `Machine Status`).

### 5.2 Dashboard View
- **4 KPI Cards:** `Pending Withdrawals` (Action Required), `Online Machines` (Active Units), `Total Points` (Lifetime Value), `Recycled Weight` (kg).
- **3 Activity Panels:** `Live Recycling`, `Cleaning Logs`, `Withdrawals` + `System Health` footer and `Open Big Data Platform` button.

### 5.3 Submission Verification & Split-Photo Audit Modal
- **Controls:** `Cleanup`, `Fetch & Verify`, `Force Sync`, Search input, Waste Type filter, Date range filter, and status tabs (`PENDING`, `VERIFIED`, `REJECTED`).
- **Table Columns:** `SUBMITTED AT`, `USER` (Name + Phone), `ID` (`#00129384`), `MACHINE`, `TYPE`, `PHOTOS`, `USER WGT` (kg), `BIN LVL` (kg), `ACTIONS` (`[✓ Approve]`, `[✏️ Correct Modal]`, `[✕ Reject]`).
- **Correct Submission Modal:**
  - **Left Side:** Split view showing `BEFORE (BIN STATE)` and `AFTER (SUBMISSION)` camera snapshots parsed from the comma-separated `snapshot_urls` string.
  - **Right Side:** Displays `WASTE TYPE`, `RATE` (pts/kg), editable `Actual Delivery Weight (KG)` input (with `Machine: X kg` reference), live-calculated `Points Awarded`, and `Reject` / `Cancel` / `Confirm` buttons.

### 5.4 Machine Status View
- **Monitoring Table:** Displays `STATUS & ZONE` (`Online`, `Bin Full`, `Maintenance` + Area zone), `LOCATION DETAILS`, `DEVICE ID`, dual-compartment `BIN LEVEL (%)` and `CURRENT WEIGHT` bars (`Plastic & Can`, `Paper`, `UCO (Oil)`), interactive `FORCE OFFLINE` toggle (`AUTO MODE` vs `MAINTENANCE`), and `SUPPORT` phone number.

### 5.5 Withdrawal Requests & Withdrawal Details Modal
- **Controls:** `Export All` (CSV), `Global Audit`, `Refresh`, Search/Filter bar, and status tabs (`Pending`, `Paid / History`, `Rejected`).
- **Withdrawal Details Modal:** Clicking a withdrawal request opens a modal displaying all user-submitted payout fields:
  - `Bank Name`, `Account No.`, `Account Holder Name (Full Name per IC)`, `Points Deducted`, `RM Payout Value`, and `Request Date`.
  - **Actions:** `Approve / Mark as Paid` or `Reject & Refund Points` (automatically credits `amount_points` back to `users.points_balance`).

## 6. Software Architecture & Directory Structure
OpenRVM v2.0 uses a **Hybrid Monorepo Architecture**:
- **Backend (`services/openrvm-api/app/`):** Clean Layered Architecture separating `core/` (DB/Redis/Security), `models/` (SQLAlchemy ORM), `schemas/` (Pydantic DTOs), `services/` (Background Vendor Sync Worker), and `api/` (Modular FastAPI Routers for Auth, Recycler, and Admin).
- **Frontend (`services/openrvm-ui/src/`):** Feature-Based Modular Architecture separating `core/` (`types.ts`, `api.ts`) from domain modules (`modules/auth/`, `modules/recycler/`, and `modules/admin/`).
