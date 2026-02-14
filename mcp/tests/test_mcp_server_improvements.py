import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from auth.security import verify_api_key
from config.settings import settings
from mcp_server import mcp_app


class MCPServerImprovementTests(unittest.TestCase):
    def setUp(self) -> None:
        mcp_app.dependency_overrides[verify_api_key] = lambda: SimpleNamespace(
            user_id=1,
            key_type="test",
        )

    def tearDown(self) -> None:
        mcp_app.dependency_overrides.clear()

    def test_tools_list_includes_hybrid_overview(self) -> None:
        with TestClient(mcp_app) as client:
            response = client.post("/tools/list")

        self.assertEqual(response.status_code, 200)
        names = {tool["name"] for tool in response.json()}
        self.assertIn("hybrid_patent_overview", names)

    def test_metrics_endpoint_returns_aggregates(self) -> None:
        with TestClient(mcp_app) as client:
            client.get("/health")
            response = client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("requests_total", payload)
        self.assertIn("avg_latency_ms", payload)
        self.assertIn("by_path", payload)


class MCPAuthTests(unittest.IsolatedAsyncioTestCase):
    async def test_verify_api_key_accepts_master_key(self) -> None:
        old_master = settings.MCP_API_KEY
        had_allow_master = hasattr(settings, "MCP_ALLOW_MASTER_KEY")
        had_allow_non_db = hasattr(settings, "MCP_AUTH_ALLOW_NON_DB_KEYS")
        old_allow_master = getattr(settings, "MCP_ALLOW_MASTER_KEY", True)
        old_allow_non_db = getattr(settings, "MCP_AUTH_ALLOW_NON_DB_KEYS", False)
        settings.MCP_API_KEY = "master-key"
        object.__setattr__(settings, "MCP_ALLOW_MASTER_KEY", True)
        object.__setattr__(settings, "MCP_AUTH_ALLOW_NON_DB_KEYS", False)

        try:
            session = AsyncMock()
            result = await verify_api_key(
                api_key_str="master-key",
                bearer_credentials=None,
                session=session,
            )
            self.assertEqual(result.key_type, "master")
        finally:
            settings.MCP_API_KEY = old_master
            if had_allow_master:
                object.__setattr__(settings, "MCP_ALLOW_MASTER_KEY", old_allow_master)
            else:
                object.__delattr__(settings, "MCP_ALLOW_MASTER_KEY")

            if had_allow_non_db:
                object.__setattr__(
                    settings,
                    "MCP_AUTH_ALLOW_NON_DB_KEYS",
                    old_allow_non_db,
                )
            else:
                object.__delattr__(settings, "MCP_AUTH_ALLOW_NON_DB_KEYS")


if __name__ == "__main__":
    unittest.main()
