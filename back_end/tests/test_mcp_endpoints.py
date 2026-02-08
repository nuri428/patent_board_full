import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, patch, AsyncMock

from app.main import app
from app.models import User
from app.schemas.mcp import (
    ProxyResult,
)


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.is_active = True
    return user


@pytest.fixture
def client(mock_user, mock_db_session):
    """Test client with mocked dependencies."""
    from app.api.deps import get_db, get_current_active_user

    # Use dependency_overrides for reliability
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    with patch("app.api.v1.endpoints.mcp.get_mcp_crud") as mock_crud:
        crud_instance = Mock()
        mock_crud.return_value = crud_instance
        crud_instance.get_by_user = AsyncMock(
            return_value=[
                Mock(
                    id=1,
                    name="test",
                    key_type="all",
                    api_key="test-api-key",
                    is_active=True,
                    created_at="2023-01-01T00:00:00",
                )
            ]
        )

        with TestClient(app) as c:
            yield c

    # Clean up overrides
    app.dependency_overrides.clear()


class TestMCPKeyEndpoints:
    """Test MCP API key management endpoints."""

    def test_list_keys_empty(self, client):
        """Test listing API keys when none exist."""
        with patch("app.api.v1.endpoints.mcp.get_mcp_crud") as mock_crud:
            crud_instance = Mock()
            mock_crud.return_value = crud_instance
            crud_instance.get_by_user = AsyncMock(return_value=[])

            response = client.get("/api/v1/mcp/keys")
            assert response.status_code == 200
            assert response.json() == []

    def test_list_keys_with_keys(self, client):
        """Test listing API keys when they exist."""
        from datetime import datetime

        with patch("app.api.v1.endpoints.mcp.get_mcp_crud") as mock_crud:
            k1 = Mock(
                id=1,
                key_type="simple",
                api_key="key1",
                is_active=True,
                created_at=datetime(2023, 1, 1),
                last_used_at=None,
            )
            k1.name = "key1"
            k2 = Mock(
                id=2,
                key_type="all",
                api_key="key2",
                is_active=True,
                created_at=datetime(2023, 1, 2),
                last_used_at=None,
            )
            k2.name = "key2"
            mock_keys = [k1, k2]
            crud_instance = Mock()
            mock_crud.return_value = crud_instance
            crud_instance.get_by_user = AsyncMock(return_value=mock_keys)

            response = client.get("/api/v1/mcp/keys")
            assert response.status_code == 200
            assert len(response.json()) == 2

    def test_generate_key(self, client):
        """Test generating a new API key."""
        from datetime import datetime

        with patch("app.api.v1.endpoints.mcp.get_mcp_crud") as mock_crud:
            mock_result = Mock(
                id=1,
                key_type="simple",
                api_key="new-api-key",
                is_active=True,
                created_at=datetime(2023, 1, 1),
                last_used_at=None,
            )
            mock_result.name = "Test Key"
            crud_instance = Mock()
            mock_crud.return_value = crud_instance
            crud_instance.create = AsyncMock(return_value=mock_result)

            key_data = {"name": "Test Key", "description": "Test API key"}
            response = client.post("/api/v1/mcp/keys", json=key_data)

            assert response.status_code == 200
            assert response.json()["api_key"] == "new-api-key"


class TestProxyEndpoints:
    """Test proxy endpoints using mocked MCPService."""

    @patch("app.api.v1.endpoints.mcp.MCPService")
    def test_proxy_tool_call_success(self, mock_service_class, client):
        mock_service = AsyncMock()
        mock_service.call_tool.return_value = ProxyResult(
            status="success", data={"result": "ok"}, confidence="High", source="MCP"
        )
        mock_service_class.return_value = mock_service

        response = client.post(
            "/api/v1/mcp/proxy",
            json={"tool_name": "test_tool", "arguments": {"arg1": "val1"}},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    @patch("app.api.v1.endpoints.mcp.MCPService")
    def test_semantic_search_success(self, mock_service_class, client):
        """Test successful semantic search proxy call."""
        mock_service = AsyncMock()
        mock_service.semantic_search.return_value = ProxyResult(
            status="success",
            data=[{"id": "1", "title": "Test Patent"}],
            confidence="High",
            source="OpenSearch",
        )
        mock_service_class.return_value = mock_service

        request_data = {
            "query": "machine learning",
            "limit": 10,
            "similarity_threshold": 0.7,
        }

        response = client.post("/api/v1/mcp/proxy/semantic-search", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["confidence"] == "High"
        assert response.json()["source"] == "OpenSearch"

    def test_semantic_search_no_api_key(self, client):
        """Test semantic search when no API key is found."""
        with patch("app.api.v1.endpoints.mcp.get_mcp_crud") as mock_crud:
            crud_instance = Mock()
            mock_crud.return_value = crud_instance
            crud_instance.get_by_user = AsyncMock(return_value=[])

            request_data = {
                "query": "machine learning",
                "limit": 10,
                "similarity_threshold": 0.7,
            }

            response = client.post(
                "/api/v1/mcp/proxy/semantic-search", json=request_data
            )

            assert response.status_code == 403
            assert response.json()["detail"] == "No active MCP API Key found"

    @patch("app.api.v1.endpoints.mcp.MCPService")
    def test_semantic_search_mcp_error(self, mock_service_class, client):
        """Test semantic search when MCP server returns an error, triggering fallback."""
        mock_service = AsyncMock()
        mock_service.semantic_search.side_effect = Exception("MCP Server Error")
        mock_service_class.return_value = mock_service

        request_data = {
            "query": "machine learning",
            "limit": 10,
            "similarity_threshold": 0.7,
        }

        response = client.post("/api/v1/mcp/proxy/semantic-search", json=request_data)

        assert response.status_code == 200
        assert response.json()["source"] == "Backend-Test-Fallback"

    @patch("app.api.v1.endpoints.mcp.MCPService")
    def test_network_analysis_success(self, mock_service_class, client):
        """Test successful network analysis proxy call."""
        mock_service = AsyncMock()
        mock_service.network_analysis.return_value = ProxyResult(
            status="success",
            data={
                "nodes": [{"id": "1", "label": "Node 1"}],
                "edges": [{"from": "1", "to": "2"}],
            },
            confidence="Medium",
            source="Neo4j",
        )
        mock_service_class.return_value = mock_service

        request_data = {
            "company_name": "Test Company",
            "analysis_options": ["centrality", "community"],
        }

        response = client.post("/api/v1/mcp/proxy/network-analysis", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["confidence"] == "Medium"
        assert response.json()["source"] == "Neo4j"

    @patch("app.api.v1.endpoints.mcp.MCPService")
    def test_network_analysis_timeout(self, mock_service_class, client):
        """Test network analysis with timeout handling."""
        mock_service = AsyncMock()
        mock_service.network_analysis.side_effect = Exception("Request timeout")
        mock_service_class.return_value = mock_service

        request_data = {"company_name": "Test Company"}

        response = client.post("/api/v1/mcp/proxy/network-analysis", json=request_data)

        assert response.status_code == 200
        assert response.json()["source"] == "Backend-Test-Fallback"

    @patch("app.api.v1.endpoints.mcp.MCPService")
    def test_tech_mapping_success(self, mock_service_class, client):
        """Test successful technology mapping proxy call."""
        mock_service = AsyncMock()
        mock_service.technology_mapping.return_value = ProxyResult(
            status="success",
            data=[
                {
                    "patent_id": "US123456",
                    "technology_name": "Machine Learning",
                    "confidence": 0.92,
                    "method": "IPC_MAPPING",
                }
            ],
            confidence="High",
            source="Neo4j-V2-Mapper",
        )
        mock_service_class.return_value = mock_service

        request_data = {
            "patent_id": "US123456",
            "technology_id": "TECH123",
            "confidence": 0.8,
            "method": "test",
            "analysis_run_id": "RUN123",
        }

        response = client.post(
            "/api/v1/mcp/proxy/technology-mapping", json=request_data
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["confidence"] == "High"
        assert response.json()["source"] == "Neo4j-V2-Mapper"

    def test_tech_mapping_invalid_input(self, client):
        """Test technology mapping with invalid input."""
        # Missing required patent_id
        request_data = {
            "technology_name": "Machine Learning",
            "confidence_threshold": 0.8,
        }

        response = client.post(
            "/api/v1/mcp/proxy/technology-mapping", json=request_data
        )

        assert response.status_code == 422  # Validation error


class TestMCPServiceLogic:
    """Test internal logic of MCPService."""

    def test_process_semantic_response(self):
        """Test processing semantic search response."""
        from app.services.mcp_service import MCPService

        service = MCPService(api_key="test")

        raw_data = {
            "status": "success",
            "data": [{"id": "1", "title": "Test Patent", "score": 0.85}],
            "metadata": {"engine": "OpenSearch", "confidence": "High"},
        }

        result = service._process_response("search_kr_patents", raw_data)

        assert result.status == "success"
        assert result.confidence == "High"
        assert result.source == "OpenSearch"
        assert "interpretation_note" in result.model_dump()

    def test_process_response_sampling(self):
        """Test processing network analysis response with sampling."""
        from app.services.mcp_service import MCPService

        service = MCPService(api_key="test")

        raw_data = {
            "status": "success",
            "data": {
                "nodes": [{"id": str(i), "label": f"Node {i}"} for i in range(40)],
                "edges": [],
            },
        }

        result = service._process_response("network_analysis", raw_data)

        assert result.status == "success"
        assert "nodes" in result.data
        # Sampling logic: len > 30 should result in 30 nodes
        assert len(result.data["nodes"]) == 30
        assert "Showing top 30" in result.interpretation_note

    def test_process_tech_mapping_response(self):
        """Test processing technology mapping response."""
        from app.services.mcp_service import MCPService

        service = MCPService(api_key="test")

        raw_data = {
            "status": "success",
            "data": [
                {
                    "patent_id": "US123456",
                    "technology_name": "Machine Learning",
                    "confidence": 0.92,
                    "method": "IPC_MAPPING",
                }
            ],
            "metadata": {"engine": "Neo4j-V2-Mapper", "confidence": "High"},
        }

        result = service._process_response("technology_mapping", raw_data)

        assert result.status == "success"
        assert result.confidence == "High"
        assert result.source == "Neo4j-V2-Mapper"


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""

    @patch("app.api.v1.endpoints.mcp.MCPService")
    def test_full_workflow_success(self, mock_service_class, client):
        """Test complete workflow from request to response."""
        mock_service = AsyncMock()
        mock_service.semantic_search.return_value = ProxyResult(
            status="success",
            data=[{"id": "1", "title": "Test Patent"}],
            confidence="High",
            source="Test Engine",
        )
        mock_service_class.return_value = mock_service

        request_data = {
            "query": "test query",
            "limit": 10,
            "similarity_threshold": 0.7,
        }

        response = client.post("/api/v1/mcp/proxy/semantic-search", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # Verify MCPService method was called
        mock_service.semantic_search.assert_called_once()
        args, kwargs = mock_service.semantic_search.call_args
        assert args[0] == "test query"
        assert args[1] == 10

    @patch("app.api.v1.endpoints.mcp.MCPService")
    def test_mcp_server_down(self, mock_service_class, client):
        """Test behavior when MCP server is down (simulated by MCPService error)."""
        mock_service = AsyncMock()
        mock_service.semantic_search.side_effect = Exception("Connection refused")
        mock_service_class.return_value = mock_service

        request_data = {"query": "test query"}

        response = client.post("/api/v1/mcp/proxy/semantic-search", json=request_data)

        assert response.status_code == 200
        assert response.json()["source"] == "Backend-Test-Fallback"
