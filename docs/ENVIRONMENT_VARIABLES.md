# KPA Welfare Management System — Environment Variables Specification

This document details all environment variables across Backend, Web Admin, and Mobile Apps.

---

### 1. Backend Environment Variables (`.env`)

#### Application & Server
- `APP_NAME`: Application title (default: `"KPA Welfare Management System"`)
- `APP_ENV`: Deployment environment (`"development"`, `"staging"`, `"production"`)
- `APP_DEBUG`: Boolean debug flag (`true` in development, `false` in production)
- `APP_PORT`: FastAPI server listening port (`8000`)
- `API_V1_PREFIX`: API route prefix (`"/api/v1"`)

#### Security & Auth
- `SECRET_KEY`: 64-char cryptographic random secret for JWT signing
- `ALGORITHM`: JWT signing algorithm (`"HS256"`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime (`15`)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime (`30`)
- `OTP_EXPIRE_MINUTES`: Time window for OTP entry (`5`)
- `OTP_RESEND_COOLDOWN_SECONDS`: Enforced wait before OTP resend (`60`)
- `MOCK_OTP_IN_DEV`: If `true`, permits `123456` in development/testing mode

#### Database & Redis
- `DATABASE_URL`: Async PostgreSQL URL (e.g., `postgresql+asyncpg://kpa_user:kpa_pass@localhost:5432/kpa_db`)
- `DATABASE_SYNC_URL`: Sync connection URL for Alembic migrations (`postgresql://kpa_user:kpa_pass@localhost:5432/kpa_db`)
- `REDIS_URL`: Redis connection URL (`redis://localhost:6379/0`)

#### Payment Gateway (Razorpay)
- `RAZORPAY_KEY_ID`: Razorpay Public API key
- `RAZORPAY_KEY_SECRET`: Razorpay Secret key
- `RAZORPAY_WEBHOOK_SECRET`: Secret to verify Razorpay webhook signature header (`X-Razorpay-Signature`)
- `WELFARE_CONTRIBUTION_AMOUNT_INR`: Fixed per-member debit (`10.00`)

#### Notifications & Integrations
- `FIREBASE_CREDENTIALS_JSON`: JSON path or string for FCM Service Account
- `MSG91_AUTH_KEY`: MSG91 SMS gateway key
- `MSG91_SENDER_ID`: 6-character registered DLT Sender ID
- `SMTP_HOST`: Mail server hostname
- `SMTP_PORT`: Port (587 or 465)
- `SMTP_USER`: Mail auth username
- `SMTP_PASSWORD`: Mail auth password

---

### 2. Web Admin Environment Variables (`apps/web/.env`)

- `VITE_API_BASE_URL`: Base URL for the backend API (`http://localhost:8000/api/v1`)
- `VITE_RAZORPAY_KEY_ID`: Razorpay checkout public key
- `VITE_DEFAULT_LANGUAGE`: Default UI locale (`"en"`)

---

### 3. Mobile App Environment Variables (`apps/mobile/.env`)

- `EXPO_PUBLIC_API_BASE_URL`: Mobile API endpoint URL (`http://10.0.2.2:8000/api/v1` for Android emulator or LAN IP)
- `EXPO_PUBLIC_RAZORPAY_KEY_ID`: Razorpay key for mobile SDK
- `EXPO_PUBLIC_ENV`: `"development"` or `"production"`
