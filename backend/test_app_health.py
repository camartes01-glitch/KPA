import asyncio
import httpx
from app.main import app

async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        print("HEALTH_STATUS:", r.status_code)
        print("HEALTH_BODY:", r.json())
        
        r2 = await client.get("/api/v1/geo/districts")
        print("DISTRICTS_STATUS:", r2.status_code)
        print("DISTRICTS_COUNT:", len(r2.json()))

if __name__ == "__main__":
    asyncio.run(main())
