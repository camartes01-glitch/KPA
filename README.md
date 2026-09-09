# Karnataka Photography Association — Welfare Management System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev)
[![Expo](https://img.shields.io/badge/Expo-SDK51+-000020.svg)](https://expo.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org)

A secure, scalable, production-ready welfare management platform for the Karnataka Photography Association — supporting **1,000,000+ members** across Android, iOS, and Web.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Documentation](#documentation)

---

## Overview

The KPA Welfare Management System handles:

- **Member registration and management** (with digital membership cards + QR codes)
- **Welfare events** (member deaths) with automatic ₹10 contribution obligations per active member
- **Payment processing** via Razorpay (UPI, AutoPay, eMandate)
- **Multi-level role-based access** (State Head → District → Taluka → Member)
- **Push/SMS/Email notifications**
- **Reports and exports** (Excel, CSV, PDF)
- **Audit logging** for all critical actions

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Client Layer                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Mobile App   │  │  Web Admin   │                │
│  │ React Native │  │   React.js   │                │
│  │ + Expo       │  │   + Vite     │                │
│  └──────┬───────┘  └──────┬───────┘                │
└─────────┼─────────────────┼───────────────────────-─┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend (REST + OpenAPI)        │
│  Auth │ Members │ Welfare │ Payments │ Reports │ ... │
└───────┬─────────────────────────────────────────────┘
        │
   ┌────┴───────────────────────────────────┐
   │                                        │
   ▼                                        ▼
PostgreSQL (primary)                   Redis (cache + tasks)
+ Alembic migrations                   + Celery workers
```

**Roles (hierarchical):**
```
STATE_HEAD → DISTRICT_ADMIN → TALUKA_ADMIN → MEMBER
```

---

## Repository Structure

```
kpa/
├── apps/
│   ├── mobile/          # React Native + Expo (Android + iOS)
│   └── web/             # React.js Admin Panel (Vite)
├── backend/             # Python FastAPI
│   ├── app/
│   │   ├── api/         # Route handlers (v1/)
│   │   ├── core/        # Config, security, DB, logging
│   │   ├── models/      # SQLAlchemy ORM models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── repositories/# DB query layer
│   │   ├── middleware/  # Auth, rate-limiting, CORS
│   │   ├── tasks/       # Celery background tasks
│   │   ├── integrations/# Razorpay, FCM, MSG91, Email
│   │   └── utils/       # Helpers
│   ├── alembic/         # Database migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
├── database/
│   └── migrations/      # Migration history reference
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── API.md
│   ├── AUTHENTICATION.md
│   ├── RBAC.md
│   ├── PAYMENTS.md
│   ├── AUTOPAY.md
│   ├── NOTIFICATIONS.md
│   ├── DEPLOYMENT.md
│   └── ENVIRONMENT_VARIABLES.md
├── tests/
│   ├── backend/
│   ├── web/
│   └── e2e/
├── scripts/
│   ├── init_db.sql
│   └── seed.py
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose
- Git

### 1. Clone and configure

```bash
git clone <repo-url> kpa
cd kpa
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start infrastructure (PostgreSQL + Redis)

```bash
docker compose up postgres redis -d
```

### 3. Start the backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API docs available at: **http://localhost:8000/docs**

### 4. Start the web admin

```bash
cd apps/web
npm install
npm run dev
# http://localhost:5173
```

### 5. Start the mobile app

```bash
cd apps/mobile
npm install
npx expo start
```

---

## Environment Variables

See [`.env.example`](.env.example) for the full list of required variables.

See [`docs/ENVIRONMENT_VARIABLES.md`](docs/ENVIRONMENT_VARIABLES.md) for detailed descriptions.

**Required for basic local development:**

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL async connection string |
| `DATABASE_SYNC_URL` | PostgreSQL sync string (Alembic) |
| `REDIS_URL` | Redis connection string |
| `SECRET_KEY` | JWT signing secret (64+ chars) |
| `OTP_DEV_MODE=true` | Use fixed OTP in development |

**Required for full functionality:**

| Integration | Variables Needed |
|---|---|
| Razorpay | `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` |
| Supabase Storage | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` |
| Firebase FCM | `FIREBASE_SERVICE_ACCOUNT_PATH` or `FIREBASE_SERVICE_ACCOUNT_JSON` |
| MSG91 SMS | `MSG91_AUTH_KEY`, `MSG91_SENDER_ID` |
| SendGrid Email | `SENDGRID_API_KEY` |

---

## Development

### Running tests

```bash
cd backend
pytest tests/ -v
```

### Database migrations

```bash
cd backend
# Create a new migration
alembic revision --autogenerate -m "description"
# Apply migrations
alembic upgrade head
# Rollback
alembic downgrade -1
```

### Seed data

```bash
cd backend
python ../scripts/seed.py
```

---

## Testing

See [`docs/TESTING.md`](docs/TESTING.md) for the full test plan.

**Critical test:**
```
Create a welfare event → assert exactly 1 contribution record per active member
at ₹10 → verify no duplicates → verify deceased member excluded →
confirm payment status changes only via verified backend/payment-provider events.
```

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | System design and component overview |
| [Database Schema](docs/DATABASE_SCHEMA.md) | All tables, columns, indexes |
| [API Reference](docs/API.md) | Endpoint catalogue |
| [Authentication](docs/AUTHENTICATION.md) | OTP flow, JWT, sessions |
| [RBAC](docs/RBAC.md) | Roles, permissions, geographic scope |
| [Payments](docs/PAYMENTS.md) | Razorpay integration, state machine |
| [AutoPay](docs/AUTOPAY.md) | Mandate flow, UPI AutoPay |
| [Notifications](docs/NOTIFICATIONS.md) | FCM, SMS, Email |
| [Deployment](docs/DEPLOYMENT.md) | Production deployment guide |
| [Environment Variables](docs/ENVIRONMENT_VARIABLES.md) | All env vars documented |

---

## License

Proprietary — Karnataka Photography Association. All rights reserved.
