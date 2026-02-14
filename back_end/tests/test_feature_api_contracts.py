from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


def _mock_user(admin: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        email="test@example.com",
        is_active=True,
        role="admin" if admin else "user",
        is_admin=admin,
    )


def _mock_db() -> Mock:
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    return session


def test_cleanup_health_contract() -> None:
    from app.api.deps import get_current_active_user
    from app.auto_cleanup_scheduler import get_scheduler

    scheduler = Mock()
    scheduler.is_running.return_value = True

    app.dependency_overrides[get_current_active_user] = lambda: _mock_user(
        admin=True
    )
    app.dependency_overrides[get_scheduler] = lambda: scheduler

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/cleanup/health")

        assert response.status_code == 200
        payload = response.json()
        assert "scheduler_running" in payload
        assert "last_cleanup_time" in payload
        assert "last_cleanup_stats" in payload
    finally:
        app.dependency_overrides.clear()


def test_session_favorites_create_contract() -> None:
    from app.api.deps import get_current_active_user
    from app.api.v1.endpoints import session_favorites

    app.dependency_overrides[get_current_active_user] = lambda: _mock_user(
        admin=False
    )
    app.dependency_overrides[session_favorites.get_db] = _mock_db

    favorite = SimpleNamespace(
        id="fav-1",
        user_id=1,
        session_id="session-1",
        notes="hello",
        keywords=["ai", "patent"],
        is_pinned=False,
        created_at=datetime.now(timezone.utc),
        updated_at=None,
    )

    with patch(
        "app.api.v1.endpoints.session_favorites.get_session_favorite_crud"
    ) as mock_get_crud:
        crud = Mock()
        crud.get_by_user_and_session = AsyncMock(return_value=None)
        crud.create = AsyncMock(return_value=favorite)
        mock_get_crud.return_value = crud

        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/session-favorites",
                    json={
                        "session_id": "session-1",
                        "notes": "hello",
                        "keywords": ["ai", "patent"],
                        "is_pinned": False,
                    },
                )

            assert response.status_code == 201
            payload = response.json()
            assert payload["id"] == "fav-1"
            assert payload["session_id"] == "session-1"
            assert payload["keywords"] == ["ai", "patent"]
        finally:
            app.dependency_overrides.clear()


def test_multi_modal_query_count_validation_contract() -> None:
    from app.api.deps import get_current_active_user
    from app.api.v1.endpoints import multi_modal_chat

    app.dependency_overrides[get_current_active_user] = lambda: _mock_user(
        admin=False
    )
    app.dependency_overrides[multi_modal_chat.get_db] = _mock_db

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/multi-modal",
            json={
                "queries": ["q1", "q2", "q3"],
            },
        )

    try:
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert any(
            "at most 2 items" in str(item.get("msg", "")) for item in detail
        )
    finally:
        app.dependency_overrides.clear()


def test_mcp_fallback_disabled_in_production() -> None:
    from app.api.deps import get_current_active_user
    from app.api.v1.endpoints import mcp

    app.dependency_overrides[get_current_active_user] = lambda: _mock_user(
        admin=False
    )
    app.dependency_overrides[mcp.get_db] = _mock_db

    with patch("app.api.v1.endpoints.mcp.get_mcp_crud") as mock_crud, patch(
        "app.api.v1.endpoints.mcp.MCPService"
    ) as mock_service_class, patch(
        "app.api.v1.endpoints.mcp.settings"
    ) as mock_settings:
        key = SimpleNamespace(api_key="k1")
        crud = Mock()
        crud.get_by_user = AsyncMock(return_value=[key])
        mock_crud.return_value = crud

        mcp_service = AsyncMock()
        mcp_service.semantic_search.side_effect = Exception(
            "Connection refused"
        )
        mock_service_class.return_value = mcp_service

        mock_settings.ENVIRONMENT = "production"
        mock_settings.MCP_ENABLE_TEST_FALLBACK = False
        mock_settings.MCP_FALLBACK_ALLOW_NON_PROD = True
        mock_settings.MCP_SERVER_URL = "http://localhost:8082"

        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/mcp/proxy/semantic-search",
                    json={
                        "query": "battery",
                        "limit": 5,
                        "similarity_threshold": 0.7,
                    },
                )

            assert response.status_code == 503
            assert (
                response.json()["detail"]
                == "MCP service unavailable and fallback is disabled"
            )
        finally:
            app.dependency_overrides.clear()
