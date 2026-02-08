import asyncio
import sys
import os
import httpx

sys.path.append(os.getcwd())

# Configuration
BASE_URL = "http://localhost:8003"
API_KEY = "test-key-123456"  # Using the key we inserted earlier


async def test_server():
    print(f"--- Testing MCP Server at {BASE_URL} ---")

    headers = {"X-API-Key": API_KEY}

    async with httpx.AsyncClient(
        base_url=BASE_URL, headers=headers, timeout=10.0
    ) as client:
        try:
            # 1. Health Check
            print("\n[1] Health Check...")
            resp = await client.get("/health")
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json()}")
            assert resp.status_code == 200

            # 2. List Tools
            print("\n[2] List Tools...")
            resp = await client.post("/tools/list")
            if resp.status_code != 200:
                print(f"Error: {resp.text}")
            assert resp.status_code == 200
            tools = resp.json()
            print(f"Tools found: {[t['name'] for t in tools]}")

            # 3. Search Foreign Patents
            print("\n[3] Search Foreign Patents (Query: 'signal')...")
            search_payload = {"query": "signal", "country_code": "US", "limit": 5}
            resp = await client.post(
                "/tools/search_foreign_patents", json=search_payload
            )
            if resp.status_code != 200:
                print(f"Error: {resp.text}")
            assert resp.status_code == 200
            data = resp.json()
            print(f"Count: {data['count']}")
            if data["count"] > 0:
                print(
                    f"Sample: {data['patents'][0]['title']} ({data['patents'][0]['id']})"
                )

            # 4. Search KR Patents
            print("\n[4] Search KR Patents (Query: '제어')...")
            kr_payload = {"query": "제어", "limit": 5}
            resp = await client.post("/tools/search_kr_patents", json=kr_payload)
            if resp.status_code != 200:
                print(f"Error: {resp.text}")
            assert resp.status_code == 200
            data = resp.json()
            print(f"Count: {data['count']}")
            if data["count"] > 0:
                print(
                    f"Sample: {data['patents'][0]['title']} ({data['patents'][0]['id']})"
                )

            # 5. Get Details
            print("\n[5] Get Details (Foreign)...")
            # Use specific known ID if possible, otherwise use one from search
            target_id = "US08447724"  # From previous test
            details_payload = {"patent_id": target_id, "type": "foreign"}
            resp = await client.post("/tools/get_patent_details", json=details_payload)
            if resp.status_code != 200:
                print(f"Error: {resp.text}")
            assert resp.status_code == 200
            data = resp.json()
            print(f"ID: {data['id']}")
            print(
                f"Raw Details Keys: {list(data['raw_details'].keys()) if data.get('raw_details') else 'None'}"
            )

        except AssertionError as e:
            print(f"Assertion Failed: {e}")
            raise
        except Exception as e:
            print(f"Test Failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(test_server())
