import asyncio
import sys
import os
import httpx

sys.path.append(os.getcwd())

# Docker mapped port for MCP (default to external 8081, but support internal 8080)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8081")
API_KEY = "test-key-123456"


async def test_docker_server():
    print(f"--- Testing Dockered MCP Server at {BASE_URL} ---")

    headers = {"X-API-Key": API_KEY}

    async with httpx.AsyncClient(
        base_url=BASE_URL, headers=headers, timeout=10.0
    ) as client:
        try:
            # 1. Health Check
            print("\n[1] Health Check...")
            resp = await client.get("/health")
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Response: {resp.json()}")

            # 2. List Tools
            print("\n[2] List Tools...")
            resp = await client.post("/tools/list")
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                tools = resp.json()
                print(f"Tools found: {[t['name'] for t in tools]}")

            # 3. Search Foreign Patents
            print("\n[3] Search Foreign Patents (US)...")
            payload = {"query": "system", "country_code": "US", "limit": 1}
            resp = await client.post("/tools/search_foreign_patents", json=payload)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Count: {data.get('count')}")

        except Exception as e:
            print(f"Test Failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_docker_server())
