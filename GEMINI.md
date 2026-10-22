# OpenRVM Project Rules, Architecture & System Context

You are an expert AI software engineer assisting in the development of OpenRVM v2.0, a cloud-native smart recycling (2-Bin Dry RVM) and Used Cooking Oil (UCO) platform.

## 🏛️ 1. Architectural Pattern (Hybrid Monorepo)
We strictly follow a **Hybrid Architecture**:
1. **Infrastructure Root (`~/openrvm-cloud/`):** Containerized Monorepo managed via Docker Compose.
2. **Backend (`services/openrvm-api/app/`):** **Clean 3-Tier Layered Architecture**:
   - `core/`: Configuration (`config.py`), Database & Redis connections (`database.py`), and Auth/Crypto utilities (`security.py`).
   - `models/`: SQLAlchemy PostgreSQL 16 ORM entities (`entities.py`).
   - `schemas/`: Pydantic v2 Data Transfer Objects (`dto.py`).
   - `services/`: Business logic and background vendor polling reconciliation (`sync_worker.py`).
   - `api/`: Modular `APIRouter` controllers (`auth_routes.py`, `recycler_routes.py`, `admin_routes.py`).
3. **Frontend (`services/openrvm-ui/src/`):** **Feature-Based (Domain-Driven) Modular Architecture**:
   - `core/`: Shared TypeScript interfaces (`types.ts`) and centralized API client (`api.ts`).
   - `modules/auth/`: Welcome, Google Sign-In, and 4-Digit Phone OTP screens.
   - `modules/recycler/`: Mobile-first Recycler views (`HomeView.vue`, `WithdrawView.vue`, `HistoryView.vue`, `ProfileView.vue`).
   - `modules/admin/`: Desktop Merchant Admin Platform views (`AdminLayout.vue`, `DashboardTab.vue`, `SubmissionsTab.vue`, `CorrectModal.vue`, `MachinesTab.vue`, `WithdrawalsTab.vue`, `PayoutModal.vue`).

## 🛠️ 2. Tech Stack & Infrastructure Rules
- **Backend:** Python 3.12 (FastAPI) + SQLAlchemy 2.0 (`postgresql+psycopg2://`) + `redis-py` + `httpx`.
- **Frontend:** Vue 3 (`<script setup lang="ts">`) + Vite + Tailwind CSS.
- **Database:** Self-hosted PostgreSQL 16 (`openrvm_db`) and Redis 7 (`openrvm_redis`). Never use Vercel Serverless or cloud Supabase SDKs.
- **Ingress:** Domain-based routing via NGINX (`rvm.ariff.lab` -> Recycler App, `admin.rvm.ariff.lab` -> Merchant Admin Platform).

## ✍️ 3. Strict Coding & Business Logic Guidelines
1. **Delayed Point Escrow:** All hardware drops start as `audit_status = "PENDING"` and credit `users.pending_points`. Only move points to withdrawable `users.points_balance` when an Admin approves or corrects the submission.
2. **Camera Snapshot Strings:** Dry RVM (`DRY_2BIN`) submissions include `snapshot_urls` formatted as `"before_url,after_url"`. UCO (`UCO_OIL`) submissions have `snapshot_urls = null`.
3. **Type Safety & Clean Code:** Keep files modular (<250 lines per file). Use strict TypeScript interfaces from `src/core/types.ts`.
4. **Container Security:** All Dockerfiles must execute as non-root `appuser` (UID 1001).
