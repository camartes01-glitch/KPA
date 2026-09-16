# KPA Mobile Application Build Report (Android APK & iOS)

**Date:** 2026-09-16  
**Application Directory:** `D:\KPA\apps\mobile`  
**Expo SDK:** `57.0.23` (Runtime `51.0.0`)  
**EAS CLI Version:** `24.6.0`  

---

## 1. Executive Summary

Preflight verification and build configurations have been completed for both Android and iOS platforms.

- **TypeScript Preflight (`npx tsc --noEmit`):** **PASSED** (0 errors).
- **Expo Doctor Preflight (`npx expo-doctor`):** **PASSED** (17/17 checks passed, no issues detected).
- **EAS CLI:** Installed and verified (`eas-cli/24.6.0`).
- **EAS Configuration (`eas.json`):** Configured with a `preview` profile targeting **standalone APK** (`buildType: "apk"`) for Android and **internal distribution** for iOS.
- **API URL Environment Isolation:** Configured so release/preview builds target the production backend `https://api.kpawelfare.org/api/v1` rather than the local LAN IP (`192.168.29.212`).
- **Expo Account Authentication Status:** **NOT LOGGED IN**. EAS cloud builds require an authenticated Expo account to provision cloud builder resources and keystores.

---

## 2. Preflight & Configuration Matrix

| Check / Setting | Expected | Verified Value | Status |
| :--- | :--- | :--- | :--- |
| **TypeScript Validation** | Zero errors | Exited with code 0 | **PASSED** |
| **Expo Doctor Validation** | 17/17 checks | 17/17 checks passed | **PASSED** |
| **Android Package Name** | `org.kpa.welfare` | `org.kpa.welfare` | **CONFIRMED** |
| **iOS Bundle Identifier** | `org.kpa.welfare` | `org.kpa.welfare` | **CONFIRMED** |
| **iOS Tablet Support** | `true` | `supportsTablet: true` | **CONFIRMED** |
| **Release API URL** | Production URL | `https://api.kpawelfare.org/api/v1` | **CONFIGURED** |
| **Dev API URL** | LAN IPv4 | `http://192.168.29.212:8000/api/v1` | **CONFIGURED** |
| **Android Build Type** | Installable APK | `buildType: "apk"` in `eas.json` | **CONFIGURED** |
| **EAS CLI Installed** | Yes | `eas-cli/24.6.0` | **CONFIRMED** |
| **Expo User Session** | Active session | `Not logged in` | **ACTION REQUIRED** |

---

## 3. Build Profiles Configuration (`eas.json`)

The following `eas.json` was created in `D:\KPA\apps\mobile` to ensure the preview build generates an installable `.apk` file (rather than an app bundle `.aab`) and points strictly to the production API:

```json
{
  "cli": {
    "version": ">= 12.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "http://192.168.29.212:8000/api/v1"
      }
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      },
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.kpawelfare.org/api/v1"
      }
    },
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.kpawelfare.org/api/v1"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

---

## 4. Platform Status & Required Account Actions

### 4.1 Android Build Status
- **Build Status:** **Awaiting EAS User Authentication**.
- **Package Name:** `org.kpa.welfare`
- **Build Type:** Standalone APK (`preview` profile).
- **Target API:** `https://api.kpawelfare.org/api/v1`
- **Keystore:** EAS can automatically generate and manage the Android upload keystore on first build.

### 4.2 iOS Build Status
- **Build Status:** **Awaiting EAS & Apple Developer Credentials**.
- **Bundle Identifier:** `org.kpa.welfare`
- **Distribution Type:** Internal Distribution (Ad Hoc / TestFlight).
- **Target API:** `https://api.kpawelfare.org/api/v1`
- **Signing Credentials:** Requires an active Apple Developer Program membership (`$99/year`) to sign the `.ipa` binary for physical iPhone installation.
- *(Note: On Windows, local iOS simulator builds are not supported; all iOS builds must be executed via EAS Cloud).*

---

## 5. Exact Next Steps to Trigger Builds

In accordance with strict security rules, **never paste your Expo or Apple credentials in chat**. Execute the following commands in your terminal:

### Step 1: Log in to Expo EAS
Open PowerShell or Command Prompt and run:
```powershell
cd D:\KPA\apps\mobile
npx eas-cli login
```
*(Enter your Expo username/email and password interactively in your shell).*

### Step 2: Initialize EAS Project (First-Time Only)
```powershell
npx eas-cli project:init
```

### Step 3: Run Android APK Build
```powershell
npx eas-cli build --platform android --profile preview
```
- EAS will prompt to generate a new Android keystore: select **Yes** (EAS managed).
- Once started, EAS will provide a real-time web URL (e.g., `https://expo.dev/accounts/[user]/projects/kpa-welfare/builds/[build-id]`).
- When the build finishes, EAS outputs the direct download link for the `.apk` file.

### Step 4: Run iOS Build
```powershell
npx eas-cli build --platform ios --profile preview
```
- EAS will prompt for your Apple Developer account login to generate the Provisioning Profile and Distribution Certificate.
- When complete, EAS will output the build page URL and installation link.

---

## 6. Git Working Directory Status

- All existing changes, configurations, and untracked files remain intact in the working tree.
- No `git commit`, `git push`, or `git reset` commands were executed.
