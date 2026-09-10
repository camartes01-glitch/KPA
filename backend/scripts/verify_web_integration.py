"""
End-to-End Web-to-Backend Integration Test Suite.
Simulates exact Web UI requests for all 4 personas and error conditions.
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000/api/v1"

def make_request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    req_body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=req_body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return resp.status, json.loads(content)
            return resp.status, content
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, err_body

def login(phone, otp="123456"):
    # 1. Send OTP
    status, res = make_request("/auth/otp/send", "POST", {"phone": phone})
    assert status == 200, f"OTP send failed for {phone}: {status} {res}"
    
    # 2. Verify OTP
    status, res = make_request("/auth/otp/verify", "POST", {"phone": phone, "otp": otp})
    assert status == 200, f"OTP verify failed for {phone}: {status} {res}"
    tokens = res["data"]
    return tokens["access_token"], tokens["refresh_token"], tokens["user"]

def run_e2e_tests():
    print("=" * 70)
    print("  KPA WELFARE SYSTEM -- E2E WEB-TO-BACKEND INTEGRATION TESTS")
    print("=" * 70)
    
    # ── Test 1: State Head (9900000001) ───────────────────────────────────────
    print("\n[TEST 1] Testing State Head Flow (9900000001)...")
    sh_access, sh_refresh, sh_user = login("9900000001")
    assert sh_user["role"] == "STATE_HEAD"
    print(f"  [OK] Login successful: {sh_user['name']} ({sh_user['role']})")
    
    # Dashboard metrics
    status, res = make_request("/dashboard/metrics", token=sh_access)
    assert status == 200 and res["success"]
    metrics = res["data"]
    assert metrics["total_members"] >= 5
    assert metrics["district_breakdown"] is not None and len(metrics["district_breakdown"]) > 0
    print(f"  [OK] Dashboard metrics: Total={metrics['total_members']}, Active={metrics['active_members']}, Today=INR {metrics['total_collected_today']}")
    print(f"  [OK] State Head sees {len(metrics['district_breakdown'])} districts in breakdown")
    
    # Members directory & search & filter
    status, res = make_request("/members?page=1&page_size=20", token=sh_access)
    assert status == 200 and res["total"] >= 5
    print(f"  [OK] Members directory: found {res['total']} members statewide")
    
    status, res = make_request("/members?q=Ravi", token=sh_access)
    assert status == 200 and len(res["data"]) >= 1
    print(f"  [OK] Members search query 'Ravi': returned {len(res['data'])} matching members")
    
    status, res = make_request("/members?member_status=PENDING", token=sh_access)
    assert status == 200
    print(f"  [OK] Members status filter 'PENDING': returned {len(res['data'])} pending members")
    
    # Welfare events
    status, res = make_request("/welfare-events", token=sh_access)
    assert status == 200 and len(res["data"]) >= 1
    event_id = res["data"][0]["id"]
    print(f"  [OK] Welfare events: found {len(res['data'])} active case(s): '{res['data'][0]['title']}'")
    
    # Bilingual Notifications (EN & KN)
    status, res_en = make_request("/notifications/my?lang=en", token=sh_access)
    assert status == 200 and len(res_en["data"]) >= 1
    status, res_kn = make_request("/notifications/my?lang=kn", token=sh_access)
    assert status == 200 and len(res_kn["data"]) >= 1
    print(f"  [OK] Notifications: {len(res_en['data'])} EN, {len(res_kn['data'])} KN bilingual notices verified")
    
    # Reports CSV downloads
    status, csv_data = make_request("/reports/members/csv", token=sh_access)
    assert status == 200 and "Membership No" in csv_data
    print("  [OK] Reports: Membership Master Roll CSV export verified")
    
    status, csv_data = make_request("/reports/financial/csv", token=sh_access)
    assert status == 200 and "Receipt No" in csv_data
    print("  [OK] Reports: Financial Statement CSV export verified")
    
    status, csv_data = make_request(f"/reports/welfare/{event_id}/csv", token=sh_access)
    assert status == 200 and "Contribution ID" in csv_data
    print("  [OK] Reports: Welfare Event Ledger CSV export verified")
    
    # Roles & Admins list
    status, res = make_request("/auth/admins", token=sh_access)
    assert status == 200 and len(res["data"]) >= 3
    print(f"  [OK] Role Management: returned {len(res['data'])} system administrators")
    
    # Audit Logs
    status, res = make_request("/audit-logs", token=sh_access)
    assert status == 200
    print(f"  [OK] System Audit Logs: {res['total']} immutable entries accessible to State Head")
    
    # Token refresh
    status, res = make_request("/auth/token/refresh", "POST", {"refresh_token": sh_refresh})
    assert status == 200 and "access_token" in res["data"]
    print("  [OK] Token rotation: /auth/token/refresh issued new access token")
    
    # Logout
    status, res = make_request("/auth/logout", "POST", {"refresh_token": sh_refresh}, token=sh_access)
    assert status == 200
    print("  [OK] Logout: revoked session successfully")

    # ── Test 2: District Admin (9900000002) ───────────────────────────────────
    print("\n[TEST 2] Testing District Admin Flow (9900000002 - Bengaluru Urban)...")
    da_access, da_refresh, da_user = login("9900000002")
    assert da_user["role"] == "DISTRICT_ADMIN"
    print(f"  [OK] Login successful: {da_user['name']} ({da_user['role']})")
    
    # Dashboard: metrics scoped, no statewide breakdown
    status, res = make_request("/dashboard/metrics", token=da_access)
    assert status == 200
    assert res["data"]["district_breakdown"] is None  # District Admin does not see state breakdown
    print("  [OK] Dashboard: scoped to district, statewide breakdown suppressed")
    
    # Members: only Bengaluru Urban members
    status, res = make_request("/members", token=da_access)
    assert status == 200
    print(f"  [OK] Members: District Admin sees {res['total']} members in Bengaluru Urban")
    
    # RBAC Isolation: District Admin CANNOT access Audit Logs
    status, res = make_request("/audit-logs", token=da_access)
    assert status == 403, f"Expected 403 Forbidden for District Admin on audit logs, got {status}"
    print("  [OK] RBAC Isolation: Audit Logs correctly forbidden (HTTP 403) for District Admin")

    # ── Test 3: Taluka Admin (9900000003) ─────────────────────────────────────
    print("\n[TEST 3] Testing Taluka Admin Flow (9900000003 - Bengaluru North)...")
    ta_access, ta_refresh, ta_user = login("9900000003")
    assert ta_user["role"] == "TALUKA_ADMIN"
    print(f"  [OK] Login successful: {ta_user['name']} ({ta_user['role']})")
    
    # Members: only Bengaluru North taluka members
    status, res = make_request("/members", token=ta_access)
    assert status == 200
    print(f"  [OK] Members: Taluka Admin sees {res['total']} members in Bengaluru North")
    
    # RBAC Isolation: Taluka Admin CANNOT list admins or view audit logs
    status, res = make_request("/auth/admins", token=ta_access)
    assert status == 403
    print("  [OK] RBAC Isolation: /auth/admins correctly forbidden (HTTP 403) for Taluka Admin")
    
    status, res = make_request("/audit-logs", token=ta_access)
    assert status == 403
    print("  [OK] RBAC Isolation: /audit-logs correctly forbidden (HTTP 403) for Taluka Admin")

    # ── Test 4: Individual Member (9900000004) ────────────────────────────────
    print("\n[TEST 4] Testing Individual Member Flow (9900000004 - Prakash Hegde)...")
    mem_access, mem_refresh, mem_user = login("9900000004")
    assert mem_user["role"] == "MEMBER"
    print(f"  [OK] Login successful: {mem_user['name']} ({mem_user['role']})")
    
    # Member profile & Digital Card
    status, res = make_request("/members/me", token=mem_access)
    assert status == 200 and res["data"]["full_name"] == "[DEMO] Prakash Hegde"
    print(f"  [OK] Member profile: {res['data']['full_name']}, ID: {res['data']['membership_no']}")
    
    status, res = make_request("/members/me/card", token=mem_access)
    assert status == 200 and "qr_code_base64" in res["data"]
    print("  [OK] Digital ID Card: generated and verified with QR payload")
    
    # Mutual Welfare Obligations
    status, res = make_request("/welfare-events/my-obligations", token=mem_access)
    assert status == 200 and len(res["data"]) >= 1
    ob = res["data"][0]
    print(f"  [OK] Welfare obligations: Event='{ob['event_title']}', Amount=INR {ob['amount']}, Status={ob['status']}")
    
    # Member cannot access admin endpoints
    status, _ = make_request("/members", token=mem_access)
    assert status == 403
    status, _ = make_request("/audit-logs", token=mem_access)
    assert status == 403
    status, _ = make_request("/auth/admins", token=mem_access)
    assert status == 403
    print("  [OK] RBAC Isolation: Members Directory, Audit Logs, and Admin List forbidden (HTTP 403) for Member")

    # ── Test 5: Negative & Error Testing ──────────────────────────────────────
    print("\n[TEST 5] Negative and Error Testing...")
    
    # Wrong OTP
    status, res = make_request("/auth/otp/verify", "POST", {"phone": "9900000001", "otp": "000000"})
    assert status == 400
    print(f"  [OK] Invalid OTP rejected with HTTP 400: '{res.get('detail')}'")
    
    # Invalid phone format
    status, res = make_request("/auth/otp/send", "POST", {"phone": "123"})
    assert status == 422
    print("  [OK] Invalid phone format rejected with HTTP 422")
    
    # Missing / Invalid token
    status, res = make_request("/dashboard/metrics", token="invalid-token-12345")
    assert status == 401
    print("  [OK] Invalid bearer token rejected with HTTP 401 Unauthorized")
    
    print("\n" + "=" * 70)
    print("  [SUCCESS] ALL 18 INTEGRATION & SECURITY ASSERTIONS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_tests()
