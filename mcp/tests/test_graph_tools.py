import asyncio
import httpx
import os
import sys

# Standard test key
API_KEY = "test-key-123456"
# Support local or docker execution
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")


async def test_graph_tools():
    print(f"--- Testing Graph Tools at {BASE_URL} ---\n")

    headers = {"X-API-Key": API_KEY}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Competitor Analysis
        print("[1] Testing Competitor Analysis (Samsung)...")
        # In actual DB, we might not have Samsung, but we'll try generic query
        # Using a broad term if Samsung fails essentially requires knowing what IS in the DB.
        # From schema inspect we saw 'Corporation'.
        resp = await client.post(
            "/tools/graph_get_competitors",
            json={"company_name": "Samsung"},
            headers=headers,
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}...\n")

        # 2. Problem/Solution Search
        print("[2] Testing Problem Search (data)...")
        # 'data' is a common word
        resp = await client.post(
            "/tools/graph_search_by_problem_solution",
            json={"keyword": "data"},
            headers=headers,
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}...\n")

        # 3. Tech Cluster
        print("[3] Testing Tech Cluster (AI)...")
        resp = await client.post(
            "/tools/graph_get_tech_cluster",
            json={"keyword": "network"},
            headers=headers,
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}...\n")

        # 4. Find Path
        print("[4] Testing Find Path...")
        resp = await client.post(
            "/tools/graph_find_path",
            json={"start_entity": "Google", "end_entity": "Microsoft"},
            headers=headers,
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}...\n")


if __name__ == "__main__":
    asyncio.run(test_graph_tools())
