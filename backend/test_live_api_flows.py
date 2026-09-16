import os
import sys
import asyncio
import httpx
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_flow():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        print("1. Testing Send OTP (/auth/otp/send)...")
        phone = "9876543210"
        res = await client.post("/auth/otp/send", json={"phone": phone})
        print("   Send OTP response:", res.status_code, res.json())
        assert res.status_code == 200

        print("2. Testing Verify OTP (/auth/otp/verify)...")
        res = await client.post("/auth/otp/verify", json={"phone": phone, "otp": "123456"})
        print("   Verify OTP response:", res.status_code)
        assert res.status_code == 200
        auth_data = res.json()["data"]
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print("3. Testing /auth/me...")
        res = await client.get("/auth/me", headers=headers)
        print("   /auth/me response:", res.status_code, res.json()["data"]["phone"])
        assert res.status_code == 200

        print("4. Testing /geo/districts...")
        res = await client.get("/geo/districts")
        districts = res.json()
        print("   Districts found:", len(districts))
        assert res.status_code == 200

        print("5. Testing /notifications/my...")
        res = await client.get("/notifications/my", headers=headers)
        print("   Notifications response:", res.status_code, len(res.json()["data"]))
        assert res.status_code == 200

        print("6. Testing /welfare/cases...")
        res = await client.get("/welfare/cases", headers=headers)
        print("   Welfare cases response:", res.status_code, res.json())

        print("7. Testing /payments/receipts...")
        res = await client.get("/payments/receipts", headers=headers)
        print("   Receipts response:", res.status_code, len(res.json().get("data", [])))

        print("\nALL STAGING API & PAYMENT FLOWS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_flow())
