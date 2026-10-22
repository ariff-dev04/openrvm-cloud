# ♻️ OpenRVM Cloud v2.0 — Containerized Smart Waste & UCO IoT Platform

A cloud-native, microservices re-architecture of an IoT Reverse Vending Machine (**2-Bin Dry Recyclables**) and **Used Cooking Oil (UCO)** telemetry, fraud-audit, and merchant management platform. Self-hosted on a hardened **Ubuntu Server 24.04 LTS** bare-metal homelab via **Docker Compose**, **NGINX**, **FastAPI**, **PostgreSQL 16**, and **Redis 7**.

---

## 🌐 Live Portfolio Demo Links
- 📱 **User Recycler Mobile Web App:** `https://YOUR-STATIC-DOMAIN.ngrok-free.app/?portal=user`
  - *Pre-Seeded Demo Login:* Click **"Preview Pre-Seeded Demo Account (`ariff.ukm@gmail.com`)"** or sign in with your own Google email & Malaysian phone number (includes a 1-click **PDPA Delete My Account & Data** button on `/profile`).
- 🖥️ **Merchant Admin & Audit Platform:** `https://YOUR-STATIC-DOMAIN.ngrok-free.app/?portal=admin`
  - *Recruiter Read-Only Sandbox:* Click **"Enter Recruiter Read-Only Demo (`demo@openrvm.my`)"** to explore all dashboards, Before/After camera snapshots, and bank payout modals safely (`GUEST_AUDITOR` RBAC role prevents database mutation with `HTTP 403`).

---

## 🏛️ System Architecture & Engineering Highlights

### 1. Hybrid Monorepo & Clean Layered Architecture
- **Core Backend (`services/openrvm-api/app/`):** Clean 3-Tier Layered Python 3.12 (**FastAPI**) architecture separating `core/` (DB, Redis, MD5/OTP Security), `models/` (**SQLAlchemy 2.0** PostgreSQL entities), `schemas/` (**Pydantic v2** DTOs), `services/` (Async Background Polling Reconciliation Worker), and `api/` (Modular routers).
- **Frontend (`services/openrvm-ui/src/`):** Feature-Based **Vue 3 (`<script setup lang="ts">`) + Vite + Tailwind CSS** SPA compiled via a **Multi-Stage Docker Build** (`node:20-alpine` builder -> `nginx:1.27-alpine` runtime).
- **Hardware Cloud Simulator (`services/vendor-simulator/`):** Simulates third-party IoT hardware cloud endpoints (`/api/open/v1/*`), MD5 (`merchant-no + secret + timestamp`) signature verification, delta-weight calculations, and comma-separated **Before & After Bin Camera Snapshot URLs**.

### 2. Solving Real-World IoT Hardware Challenges
- **2-in-1 Station Aggregation:** Aggregates separate hardware controller IDs (`DRY_2BIN` and `UCO_OIL` fluid sensor units) into unified physical stations with embedded OpenStreetMap previews and 1-click **Google Maps / Waze** turn-by-turn navigation.
- **Hybrid Webhook + Polling Reliability (`Redis SETNX`):** Prevents missed transactions from unreliable hardware webhooks using an asynchronous background polling worker backed by **Redis 7 idempotency locks (`processed_put_v2:{put_id}`)**.
- **Delayed Point Escrow & Split-Photo Fraud Audit:** Submissions enter `users.pending_points` (`PENDING`) until a Merchant Admin reviews the **Before (Bin State) / After (Submission)** camera snapshots (or UCO capacitance sensor logs) and approves or corrects the weight.
- **Strict 1-to-1 Identity Binding & PDPA Compliance:** Enforces unique Email-to-Phone hardware binding (`HTTP 409 Conflict` duplicate protection), Redis 4-digit OTP verification (300s TTL), and 1-click cascading data deletion.

---

## 📂 Project Structure
```text
openrvm-cloud/
├── docker-compose.yml                  # Orchestrates UI, API, Simulator, Postgres 16, Redis 7, & Tunnel
├── .env.example                        # Environment variable template
├── docs/
│   ├── ARCHITECTURE.md                 # System & network topology
│   └── PRD.md                          # Product Requirements & Database Specification
└── services/
    ├── vendor-simulator/               # Containerized Mock IoT Hardware Cloud (FastAPI)
    ├── openrvm-api/                    # Clean 3-Tier Layered Core Backend (FastAPI + SQLAlchemy + Redis)
    │   └── app/{core,models,schemas,services,api}/
    └── openrvm-ui/                     # Feature-Based Modular Frontend (Vue 3 + TypeScript + Tailwind)
        └── src/{core,modules/{auth,recycler,admin}}/


