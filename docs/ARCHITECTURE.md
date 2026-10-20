# OpenRVM Cloud-Native Architecture (v2.0)

## 1. Overview & Problem Statement
OpenRVM v2.0 re-architects a legacy serverless Reverse Vending Machine (RVM) and Used Cooking Oil (UCO) platform into a self-hosted, containerized Linux microservice stack.

### Key Engineering Improvements Over v1.0:
1. **Logical 2-in-1 Station Aggregation:** Binds separate hardware controller IDs (`DRY_2BIN` and `UCO_OIL`) into unified physical stations in PostgreSQL.
2. **Hybrid Webhook + Polling Reliability:** Mitigates third-party vendor webhook drops (`api.autogcm.com` spec) using an asynchronous FastAPI background sync worker backed by **Redis 7 idempotency keys (`put_id`)**.
3. **Zero-Trust Network Segmentation:** Isolates PostgreSQL 16, Redis 7, and the Hardware Simulator inside an internal Docker bridge network (`openrvm_internal`), exposing only the Reverse Proxy ingress.

## 2. Container Topology
- `openrvm_ui`: Unified Vue 3 + TypeScript + Tailwind SPA (`/app` User Portal & `/admin` Merchant Dashboard)
- `openrvm_api`: Python 3.12 FastAPI Core Backend, MD5/HMAC Gateway & Background Sync Worker
- `openrvm_db`: PostgreSQL 16 (Persistent relational storage)
- `openrvm_redis`: Redis 7 (Idempotency locks & rate-limiting)
- `openrvm_simulator`: Containerized hardware cloud simulator implementing the 12 vendor endpoints
