# Karnataka Photography Association (KPA) Welfare Management System
## System Architecture & Technical Specifications

### 1. Architectural Overview

The KPA Welfare Management System is designed to support **1,000,000+ active members** across Karnataka state. It provides welfare event management (death/emergency mutual relief fund), payment orchestration (one-time UPI, automated debit mandates via AutoPay/eMandate), digital membership verification (QR code cards), multilingual notification broadcasts, and strict hierarchical Role-Based Access Control (RBAC).

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                               │
│                                                                         │
│  ┌───────────────────────────────────┐ ┌──────────────────────────────┐ │
│  │     Mobile App (Android / iOS)    │ │   Web Admin Panel (React)    │ │
│  │   React Native (Expo SDK 51)      │ │   Vite + TypeScript + Zustand│ │
│  │   Offline-aware, QR display       │ │   Hierarchical RBAC Dash     │ │
│  └─────────────────┬─────────────────┘ └──────────────┬───────────────┘ │
└────────────────────┼──────────────────────────────────┼─────────────────┘
                     │ HTTPS / WSS                      │ HTTPS
                     ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY / APPLICATION LAYER                    │
│                                                                         │
│  FastAPI (Python 3.11+ Async)                                            │
│  ├── Security: JWT (RS256/HS256), Refresh Rotation, Device Sessions     │
│  ├── RBAC Scopes: STATE_HEAD > DISTRICT_ADMIN > TALUKA_ADMIN > MEMBER   │
│  ├── Rate Limiting: SlowAPI / Redis Token Bucket                        │
│  └── OpenAPI / Swagger auto-documentation                               │
│                                                                         │
│  Endpoints:                                                             │
│  ├── /api/v1/auth          (OTP login, token refresh, sessions)         │
│  ├── /api/v1/members       (Registration, approval, digital card)       │
│  ├── /api/v1/welfare-events (Death benefit event creation & ledgers)    │
│  ├── /api/v1/payments      (Razorpay orders, verification, webhooks)    │
│  ├── /api/v1/autopay       (eMandate registration, recurring debits)    │
│  ├── /api/v1/notifications (FCM push, SMS, Kannada/English dispatch)   │
│  ├── /api/v1/reports       (Excel, CSV, PDF audit statements)           │
│  └── /api/v1/audit-logs    (Immutable audit trail)                      │
└────────────────────┬──────────────────────────────────┬─────────────────┘
                     │ Asyncpg pool                     │ Redis client
                     ▼                                  ▼
┌──────────────────────────────────────┐ ┌────────────────────────────────┐
│           DATA PERSISTENCE           │ │       CACHE & ASYNC QUEUE      │
│                                      │ │                                │
│ PostgreSQL 16                        │ │ Redis 7                        │
│ ├── ACID-compliant financial ledgers │ │ ├── Session & token blacklist  │
│ ├── Strict foreign key constraints   │ │ ├── Celery Task Broker         │
│ ├── Alembic schema migrations        │ │ └── Rate-limiting storage      │
│ └── Geographic indices (GIS/btree)   │ │                                │
└──────────────────────────────────────┘ └──────────────┬─────────────────┘
                                                        │
                                                        ▼
                                         ┌────────────────────────────────┐
                                         │       ASYNC BACKGROUND WORKERS │
                                         │                                │
                                         │ Celery / Python Workers        │
                                         │ ├── Bulk ₹10 ledger debits     │
                                         │ ├── AutoPay recurring triggers │
                                         │ ├── Push / SMS notifications   │
                                         │ └── PDF receipt generation     │
                                         └────────────────────────────────┘
```

---

### 2. Role-Based Access Control (RBAC) Hierarchy

Permissions flow down hierarchically based on geographic boundaries:

| Role | Scope | Key Capabilities |
| :--- | :--- | :--- |
| **STATE_HEAD** | Entire State of Karnataka (31 Districts) | Full platform administration, create Welfare Events, trigger AutoPay execution, audit logs, system configurations. |
| **DISTRICT_ADMIN** | Assigned District (e.g., Bengaluru Urban, Mysuru) | Approve member applications in district, oversee talukas, view district payment collection stats. |
| **TALUKA_ADMIN** | Assigned Taluka (e.g., Bengaluru South, Hunsur) | Verify physical member documents, onboard new photographers, send taluka notifications. |
| **AUDITOR** | State or District Read-Only | Read-only access to financial ledgers, audit trails, and reconciliation reports. |
| **MEMBER** | Self Profile | View digital membership ID + QR code, pay contributions, register AutoPay mandate, update nominee details. |

---

### 3. Welfare Event & Contribution Financial Mechanics

The heart of the KPA mutual welfare model is immediate communal relief:
1. **Event Trigger:** Upon verified demise of an active member, `STATE_HEAD` initiates a Welfare Event.
2. **Idempotent Ledger Generation:** Celery task generates an immutable `WelfareContribution` debit of ₹10 for every verified active member. A unique constraint on `(event_id, member_id)` guarantees zero duplicate debits even upon retries.
3. **Settlement Methods:**
   - **AutoPay:** Members with active eMandates are debited automatically in batch windows via Razorpay Recurring.
   - **Manual UPI/Gateway:** Members receive instant push/SMS notifications with a 1-click Razorpay payment link.
4. **Disbursement:** Collected funds (e.g., 50,000 active members × ₹10 = ₹5,00,000) are disbursed to the deceased member's verified nominee bank account with full ledger documentation.

---

### 4. High-Scale Design Decisions

- **Async Database I/O:** SQLAlchemy 2.0 async engine with `asyncpg` connection pooling to handle 10,000+ concurrent requests.
- **Batch Processing:** Contribution debits for 1,000,000 members are split into 5,000-row chunks processed by Celery worker pools.
- **Stateless Web Nodes:** JWT access tokens (15-minute expiry) verified with signature caching; refresh tokens (30 days) stored with hashed fingerprints in Redis for immediate revocation if needed.
- **Multilingual Localization:** Client-side i18n supporting Kannada (kn-IN) and English (en-IN), with localized SMS templates compliant with DLT regulations.
