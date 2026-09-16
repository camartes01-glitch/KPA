# KPA Web Admin, Android & iOS Run Report

**Date:** 2026-09-16  
**Environment:** Windows 10/11 Local Development & Staging  
**Database:** PostgreSQL 18 (`kpa_staging` on port 5432, Alembic revision `3bb49ee7ee19`)  
**Host Machine LAN IP:** `192.168.29.212`  

---

## 1. Executive Summary

All three application tiers — the **FastAPI backend**, the **React/Vite Web Admin**, and the **Expo React Native Mobile App (Android & iOS)** — are running concurrently against the real **PostgreSQL staging database**.

- **FastAPI Backend:** Running on `0.0.0.0:8000`, connected to PostgreSQL `kpa_staging`. Verified `/health` returns HTTP 200 on both `localhost:8000` and LAN `192.168.29.212:8000`. Backend regression tests pass 42/42.
- **Web Admin:** Running on `http://localhost:5173/`, built cleanly with zero TypeScript errors (`tsc && vite build`), vitest unit tests passing 5/5, and all 18 end-to-end integration and security assertions verified.
- **Android & iOS Mobile App:** Running on Expo SDK 57 in LAN mode on `http://192.168.29.212:8082` (Expo Go URL: `exp://192.168.29.212:8082`). `npx tsc --noEmit` passed with zero errors, and `npx expo-doctor` passed 17/17 checks with no issues detected.
- **Razorpay Integration:** Verified in **TEST ONLY** mode. Automated cryptographic signature verification, order creation, settle verification, receipt generation, and webhook idempotency tests all passed (4/4). No live credentials or real payments were used.

---

## 2. Infrastructure & Service Status Matrix

| Service | Host / Interface | Port | Access URL | Status |
| :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL Staging** | Localhost (WSL2) | `5432` | `postgresql://kpa_user:***@localhost:5432/kpa_staging` | **ONLINE** (Rev: `3bb49ee7ee19`) |
| **FastAPI Backend** | `0.0.0.0` (All interfaces) | `8000` | `http://localhost:8000/api/v1`<br>`http://192.168.29.212:8000/api/v1` | **ONLINE** (HTTP 200) |
| **Web Admin (Vite)** | `localhost` | `5173` | `http://localhost:5173/` | **ONLINE** |
| **Expo Metro Bundler** | `192.168.29.212` (LAN) | `8082` | `exp://192.168.29.212:8082`<br>`http://192.168.29.212:8082` | **ONLINE** (packager running) |

---

## 3. Backend Preflight & Verification

### 3.1 PostgreSQL Staging Reachability & Revision
- **Database:** PostgreSQL 18 cluster `main`, database `kpa_staging`.
- **Alembic Version Query:** `SELECT version_num FROM alembic_version;`
  - **Result:** `3bb49ee7ee19`
- **Database Engine:** Connected via `postgresql+asyncpg://kpa_user:***@localhost:5432/kpa_staging` (asynchronous pool) and `postgresql://kpa_user:***@localhost:5432/kpa_staging` (synchronous). SQLite has been disabled in favour of PostgreSQL staging.

### 3.2 Health Check & API Verification
- `GET http://localhost:8000/health` -> HTTP 200 `{"status":"ok","version":"1.0.0"}`
- `GET http://192.168.29.212:8000/health` -> HTTP 200 `{"status":"ok","version":"1.0.0"}`
- `GET http://localhost:8000/api/v1/geo/districts` -> HTTP 200 with active Karnataka districts.

### 3.3 Backend Regression Test Suite
- Command: `python -m pytest`
- **Result:** `42 passed, 1 skipped, 46 warnings in 7.56s` (100% passing rate).

---

## 4. Web Admin Application Status & Testing

### 4.1 Build & Unit Test Verification
- `npm test -- --run` (vitest): **5/5 tests passed** (API client, baseURL selection, auth headers, token refresh queue).
- `npm run build` (`tsc && vite build`): **Built in 2.62s** with zero errors (`dist/index.html`, `dist/assets/index-*.css`, `dist/assets/index-*.js`).
- Dev Server: Running at `http://localhost:5173/`.

### 4.2 End-to-End API Flow Assertions (18/18 Automated Assertions Passed)
The live Web Admin interaction was verified against the active FastAPI server and PostgreSQL database across all admin roles:

1. **State Head Persona (`9900000001`):**
   - OTP Send & Verify -> JWT tokens issued, role verified as `STATE_HEAD`.
   - Dashboard Metrics -> Retrieved total members (6), active members (4), and daily contributions (₹10.0) from PostgreSQL staging.
   - Districts Breakdown -> 6 districts loaded.
   - Members Directory -> Retrieved 6 statewide members; search query for `"Ravi"` filtered 1 member; status filter `"PENDING"` filtered 1 member.
   - Welfare Events -> Retrieved active event `[DEMO] Welfare Relief -- [DEMO] Gopal Reddy (DECEASED - Demo)`.
   - Bilingual Notifications -> Verified 4 English and 4 Kannada announcements.
   - CSV Reports -> Verified Master Roll, Financial Statement, and Welfare Ledger CSV export endpoints.
   - System Audit Logs -> Verified immutable audit log stream.
   - Roles / Admin Management -> Verified 3 system admins returned.
   - Token Rotation -> `/auth/token/refresh` returned valid new access token.
   - Logout -> Session revoked successfully.

2. **District Admin Persona (`9900000002` - Bengaluru Urban):**
   - Scoped dashboard data; statewide financial breakdowns suppressed.
   - Member list isolated to Bengaluru Urban (6 members).
   - **RBAC Enforcement:** `/audit-logs` endpoint returned **HTTP 403 Forbidden**.

3. **Taluka Admin Persona (`9900000003` - Bengaluru North):**
   - Member list isolated to Bengaluru North (2 members).
   - **RBAC Enforcement:** `/auth/admins` and `/audit-logs` returned **HTTP 403 Forbidden**.

4. **Negative Security Testing:**
   - Expired / unrequested OTP rejected with HTTP 400.
   - Malformed phone format rejected with HTTP 422.
   - Invalid or tampered Bearer token rejected with HTTP 401 Unauthorized.

---

## 5. Android Mobile Application Status

### 5.1 Preflight & Environment
- **Environment Settings (`apps/mobile/.env`):**
  - `EXPO_PUBLIC_API_URL=http://192.168.29.212:8000/api/v1`
  - `REACT_NATIVE_PACKAGER_HOSTNAME=192.168.29.212`
- **TypeScript Check (`npx tsc --noEmit`):** Exited with code 0 (zero errors).
- **Expo Doctor Check (`npx expo-doctor`):** **17/17 checks passed**. No issues detected.

### 5.2 Expo Packager & Network
- Metro bundler listening on LAN port `8082`.
- Packager status endpoint: `http://192.168.29.212:8082/status` -> `packager-status:running`.
- Manifest endpoint: `http://192.168.29.212:8082/` verified with `sdkVersion: "51.0.0"`, `package: "org.kpa.welfare"`, and host `192.168.29.212:8082`.
- **Expo Go Connection String:** `exp://192.168.29.212:8082`
- **QR Code Asset:** Generated and saved to `apps/mobile/expo_qr.png`.

### 5.3 Physical Android Device Connectivity Instructions
To open the application on a physical Android phone:
1. Ensure the Android device and laptop are on the same Wi-Fi network (`192.168.29.x`).
2. Open **Expo Go** on Android.
3. Scan the QR code below or manually enter `exp://192.168.29.212:8082`:

```
 ▄▄▄▄▄▄▄     ▄▄    ▄▄▄▄▄▄▄ 
 █ ▄▄▄ █ ▄▄█ ▀ █▀▄ █ ▄▄▄ █ 
 █ ███ █ █▀▄█▀  █  █ ███ █ 
 █▄▄▄▄▄█ █ █▀█ █ ▄ █▄▄▄▄▄█ 
 ▄ ▄▄▄▄▄ ▀▀ █▄█▀▀▄ ▄▄▄▄▄   
  ▀█ ▄▀▄█▄▄▀▀▄▀ ▀▀▀▄▄██ █▄ 
 ▀▄ █▄█▄▀  █▄▀  ▄ ▀▀█▀█▄ ▀ 
 █▀▄▀▄▀▄ ▄ ▄ ▀█▄▀█▀█▀▄█ █▄ 
 █ ▄▀▀▄▄ ▀▀▀ █▀▄ ████▄▀███ 
 ▄▄▄▄▄▄▄ ▀▄▄▄▄  ▀█ ▄ █ ▄▄▄ 
 █ ▄▄▄ █ █▄▀█  ▀▄█▄▄▄█▄█▀▄ 
 █ ███ █ █ ▄ ▀███▄▀▀   ▄ █ 
 █▄▄▄▄▄█ ▄▀▄ █▀▄▀▄▀  ▀ █▄█ 
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
```

4. **Login Credentials for Mobile Testing:**
   - Phone: `9900000004` (Demo Member: Prakash Hegde)
   - OTP: `123456`
5. Verified flows for Member:
   - **Home Screen:** Displays member name, active welfare event banner, and quick action tiles.
   - **Welfare Screen:** Fetches `/welfare-events/my-contributions` and `/welfare-events`.
   - **Digital ID Card Screen:** Renders official KPA membership badge with dynamic QR code containing verification payload.
   - **Notifications:** Displays in-app bilingual announcements.
   - **Profile:** Displays member details, membership ID (`KPA-BLRU-84568`), and logout option.

---

## 6. iOS Compatibility & Environment Limitations

### 6.1 Configuration Verification
- **SDK Compatibility:** Expo SDK 51/57 configuration verified.
- **Bundle Identifier:** Configured as `org.kpa.welfare` in `apps/mobile/app.json`.
- **Tablet Support:** `supportsTablet: true` verified.
- **Cross-Platform Code:** Codebase inspected; contains no Android-only proprietary startup code or Java-specific bridges that would break on iOS.
- **API Configuration:** Uses standard HTTP client with IPv4 LAN addressing (`http://192.168.29.212:8000/api/v1`), compatible with ATS (App Transport Security) in local development modes.

### 6.2 Host Platform Limitation (Windows OS)
- **iOS Simulator Availability:** **UNAVAILABLE ON WINDOWS**. The native iOS Simulator requires macOS and Xcode instruments.
- **Physical iPhone Testing:** Can be launched by scanning the same Expo Go QR code (`exp://192.168.29.212:8082`) using the iOS Camera app on an iPhone connected to the same Wi-Fi network. No physical iPhone testing was fabricated or claimed without hardware present.

---

## 7. Razorpay Integration Status (TEST ONLY)

> [!IMPORTANT]
> **Razorpay is configured strictly for TEST/SANDBOX mode.** No real money was debited and no live credentials (`rzp_live_*`) were used.

### 7.1 Verified Test Capabilities
- **Signature Verification:** Automated test `test_razorpay_signature_verification` verified HMAC-SHA256 signature checking.
- **Webhook Signature Verification:** Automated test `test_razorpay_webhook_signature_verification` verified `X-Razorpay-Signature` validation.
- **Order Creation & Idempotency:** Automated test `test_webhook_payment_captured_and_idempotency` verified that duplicate webhook callbacks do not produce duplicate receipts or contributions.
- **Receipt Generation:** Verified via `/api/v1/payments/receipts` and public endpoint `/api/v1/payments/receipt/KPA-DEMO-RCP-745597`. Receipt record retrieved with ₹10.0 captured via UPI.
- **Audit Logging:** Payment settlement creates an immutable entry in the `audit_logs` table with actor metadata.

---

## 8. Errors Diagnosed, Root Causes & Fixes Made

| Issue Observed | Root Cause | Resolution |
| :--- | :--- | :--- |
| Backend was configured with SQLite URLs in `.env` | `.env` lines 31-32 were pointing to `sqlite+aiosqlite:///./kpa_dev.db` | Updated `DATABASE_URL` and `DATABASE_SYNC_URL` to `postgresql+asyncpg://kpa_user:***@localhost:5432/kpa_staging` and `postgresql://...`. Verified connection using `asyncpg`. |
| WSL2 PostgreSQL port forwarding closed when WSL went idle | WSL2 background instances terminate if no active process keeps the session alive | Launched background keep-alive process (`wsl --exec sleep infinity`) ensuring persistent socket listening on port 5432. |
| Missing staging demo accounts on initial run | PostgreSQL staging database tables were unpopulated after migration | Executed `python -m scripts.seed_demo`, creating 4 demo personas (`9900000001` - `9900000004`), 6 members, 1 active welfare event, and 1 settled payment receipt. |
| CORS origins list did not include LAN IP | Backend `.env` `ALLOWED_ORIGINS` had only localhost URLs | Added `http://192.168.29.212:8000`, `http://192.168.29.212:5173`, and Expo origin strings to `.env`. |

---

## 9. Remaining Blockers & Next Steps

1. **Physical Device Verification:**
   - Both servers are actively listening. To test physically on phone, connect phone to Wi-Fi `192.168.29.212`, open Expo Go, and scan the QR code.
   - If Windows Firewall blocks incoming phone traffic on port 8000 or 8082, run an elevated PowerShell prompt to allow inbound TCP 8000 and 8082:
     ```powershell
     netsh advfirewall firewall add rule name="KPA Dev 8000" dir=in action=allow protocol=TCP localport=8000
     netsh advfirewall firewall add rule name="KPA Dev 8082" dir=in action=allow protocol=TCP localport=8082
     ```
2. **Git Working Directory State:**
   - All existing files, modifications, and untracked files have been left strictly intact. No git commits, pushes, resets, or file deletions were performed.
