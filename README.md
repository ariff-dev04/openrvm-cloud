# ♻️ OpenRVM Cloud v2.0 — Containerized Smart Waste & UCO Platform

A cloud-native re-architecture of an IoT Reverse Vending Machine (2-Bin Dry Recyclables) and Used Cooking Oil (UCO) telemetry and merchant management platform, self-hosted on an Ubuntu 24.04 LTS bare-metal homelab.

## 🏗️ Architecture & Tech Stack (v1.0 Foundation Milestone)
- **Ingress & DNS:** NGINX Reverse Proxy (`rvm.ariff.lab` & `admin.rvm.ariff.lab`) + Pi-hole v6 Infrastructure-as-Code DNS
- **Frontend (`openrvm_ui`):** Unified Vue 3 + TypeScript + Vite + Tailwind CSS compiled via Multi-Stage Docker build into `nginx:1.27-alpine`
- **Core Backend (`openrvm_api`):** Python 3.12 (FastAPI) + SQLAlchemy + Async Background Polling Reconciliation Worker
- **Database & Idempotency:** PostgreSQL 16 (`postgres:16-alpine`) + Redis 7 (`redis:7-alpine`) `SETNX` locks to prevent duplicate webhook payouts
- **Hardware Cloud Simulator (`openrvm_simulator`):** Mock IoT vendor cloud simulating 2-in-1 Station delta-weight math, MD5 (`merchant-no + secret + timestamp`) auth, and HMAC-SHA256 webhooks

## 🚀 Quick Start
```bash
chmod 600 .env
docker compose up -d --build
docker compose ps

