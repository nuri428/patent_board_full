import asyncio
import httpx
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8001/api/v1"
EMAIL = os.getenv("VERIFY_EMAIL")
PASSWORD = os.getenv("VERIFY_PASSWORD")


async def verify_endpoints():
    if not EMAIL or not PASSWORD:
        raise RuntimeError(
            "Set VERIFY_EMAIL and VERIFY_PASSWORD before running endpoint verification"
        )

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Login (JSON)
        logger.info("Attempting login...")
        try:
            response = await client.post(
                "/auth/login", json={"email": EMAIL, "password": PASSWORD}
            )
            if response.status_code != 200:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                return

            token_data = response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                logger.error("No access token in response")
                return

            headers = {"Authorization": f"Bearer {access_token}"}
            logger.info("Login successful. Token acquired.")
        except Exception as e:
            logger.error(f"Login request failed: {e}")
            return

        # 2. Check Endpoints
        endpoints = [
            ("/auth/me", "User Profile"),
            ("/admin/statistics", "Admin Statistics"),
            ("/reports/", "Reports List"),
            # ("/notifications/", "Notifications List"), # Check if root / exists in notifications
            # ("/workspaces/", "Workspaces List"), # Check if root / exists in workspaces
            ("/prompts/", "Prompts List"),
            ("/chat/history", "Chat History"),  # /chat/history
        ]

        # Verify exact paths by trial or common conventions
        # I'll try to hit list endpoints. If 404, I'll log check logic.

        for endpoint, name in endpoints:
            logger.info(f"Checking {name} ({endpoint})...")
            try:
                resp = await client.get(endpoint, headers=headers)
                if resp.status_code in [200, 201]:
                    logger.info(f"✅ {name}: OK ({resp.status_code})")
                elif resp.status_code == 404:
                    logger.warning(
                        f"⚠️ {name}: Not Found (404) - Endpoint might be missing or wrong URL"
                    )
                elif resp.status_code == 405:
                    logger.warning(
                        f"⚠️ {name}: Method Not Allowed (405) - Maybe POST required?"
                    )
                else:
                    logger.error(
                        f"❌ {name}: Failed ({resp.status_code}) - {resp.text}"
                    )
            except Exception as e:
                logger.error(f"❌ {name}: Request Error - {e}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_endpoints())
