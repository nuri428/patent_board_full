import pytest
from pydantic import ValidationError

from app.schemas.mcp import (
    SemanticSearchRequest,
    NetworkAnalysisRequest,
    TechMappingRequest,
    AnalysisWorkbenchRequest,
    MCPKeyCreate,
    MCPKeyRead,
    ProxyToolCall,
    ProxyResult,
)


class TestSemanticSearchRequest:
    """Test SemanticSearchRequest schema validation."""

    def test_valid_request(self):
        """Test valid semantic search request."""
        request = SemanticSearchRequest(
            query="machine learning algorithms",
            limit=25,
            similarity_threshold=0.8
        )
        
        assert request.query == "machine learning algorithms"
        assert request.limit == 25
        assert request.similarity_threshold == 0.8

    def test_defaults(self):
        """Test default values."""
        request = SemanticSearchRequest(query="test query")
        
        assert request.limit == 10  # Default value
        assert request.similarity_threshold == 0.7  # Default value

    def test_limit_validation(self):
        """Test limit field validation."""
        # Valid limits
        for limit in [1, 10, 50, 100]:
            request = SemanticSearchRequest(query="test", limit=limit)
            assert request.limit == limit
        
        # Invalid limits
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="test", limit=0)
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="test", limit=101)
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="test", limit=-1)

    def test_similarity_threshold_validation(self):
        """Test similarity_threshold field validation."""
        # Valid thresholds
        for threshold in [0.0, 0.5, 1.0]:
            request = SemanticSearchRequest(query="test", similarity_threshold=threshold)
            assert request.similarity_threshold == threshold
        
        # Invalid thresholds
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="test", similarity_threshold=-0.1)
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="test", similarity_threshold=1.1)

    def test_empty_query(self):
        """Test empty query validation."""
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="")

    def test_long_query(self):
        """Test very long query handling."""
        long_query = "a" * 10000
        request = SemanticSearchRequest(query=long_query)
        assert len(request.query) == 10000


class TestNetworkAnalysisRequest:
    """Test NetworkAnalysisRequest schema validation."""

    def test_valid_request(self):
        """Test valid network analysis request."""
        request = NetworkAnalysisRequest(
            company_name="Test Company",
            analysis_options=["centrality", "community"]
        )
        
        assert request.company_name == "Test Company"
        assert request.analysis_options == ["centrality", "community"]

    def test_company_name_required(self):
        """Test company_name is required."""
        with pytest.raises(ValidationError):
            NetworkAnalysisRequest(analysis_options=["centrality"])

    def test_analysis_options_defaults(self):
        """Test default analysis options."""
        request = NetworkAnalysisRequest(company_name="Test")
        assert request.analysis_options == ["centrality"]  # Default value

    def test_analysis_options_validation(self):
        """Test analysis options validation."""
        valid_options = ["centrality", "community", "path", "clustering"]
        
        for option in valid_options:
            request = NetworkAnalysisRequest(
                company_name="Test",
                analysis_options=[option]
            )
            assert option in request.analysis_options

    def test_invalid_analysis_options(self):
        """Test invalid analysis options."""
        with pytest.raises(ValidationError):
            NetworkAnalysisRequest(
                company_name="Test",
                analysis_options=["invalid_option"]
            )


class TestTechMappingRequest:
    """Test TechMappingRequest schema validation."""

    def test_valid_request(self):
        """Test valid technology mapping request."""
        request = TechMappingRequest(
            patent_id="US123456789",
            technology_name="Machine Learning",
            confidence_threshold=0.8
        )
        
        assert request.patent_id == "US123456789"
        assert request.technology_name == "Machine Learning"
        assert request.confidence_threshold == 0.8

    def test_defaults(self):
        """Test default values."""
        request = TechMappingRequest(
            patent_id="US123456789",
            technology_name="Test Technology"
        )
        
        assert request.confidence_threshold == 0.7  # Default value

    def test_patent_id_validation(self):
        """Test patent_id field validation."""
        # Valid patent IDs
        valid_ids = ["US123456", "KR2020123456", "EP123456789", "WO202012345"]
        for patent_id in valid_ids:
            request = TechMappingRequest(
                patent_id=patent_id,
                technology_name="Test"
            )
            assert request.patent_id == patent_id

    def test_confidence_threshold_validation(self):
        """Test confidence_threshold field validation."""
        # Valid thresholds
        for threshold in [0.0, 0.5, 1.0]:
            request = TechMappingRequest(
                patent_id="US123456",
                technology_name="Test",
                confidence_threshold=threshold
            )
            assert request.confidence_threshold == threshold
        
        # Invalid thresholds
        with pytest.raises(ValidationError):
            TechMappingRequest(
                patent_id="US123456",
                technology_name="Test",
                confidence_threshold=-0.1
            )
        with pytest.raises(ValidationError):
            TechMappingRequest(
                patent_id="US123456",
                technology_name="Test",
                confidence_threshold=1.1
            )


class TestAnalysisWorkbenchRequest:
    """Test AnalysisWorkbenchRequest schema validation."""

    def test_valid_request(self):
        """Test valid analysis workbench request."""
        request = AnalysisWorkbenchRequest(
            analysis_type="semantic",
            parameters={"query": "test", "limit": 10}
        )
        
        assert request.analysis_type == "semantic"
        assert request.parameters == {"query": "test", "limit": 10}

    def test_analysis_type_validation(self):
        """Test analysis_type validation."""
        valid_types = ["semantic", "network", "tech", "charts"]
        
        for analysis_type in valid_types:
            request = AnalysisWorkbenchRequest(
                analysis_type=analysis_type,
                parameters={}
            )
            assert request.analysis_type == analysis_type

    def test_invalid_analysis_type(self):
        """Test invalid analysis type."""
        with pytest.raises(ValidationError):
            AnalysisWorkbenchRequest(
                analysis_type="invalid_type",
                parameters={}
            )


class TestMCPKeyCreate:
    """Test MCPKeyCreate schema validation."""

    def test_valid_key_create(self):
        """Test valid API key creation request."""
        request = MCPKeyCreate(
            name="Test Key",
            description="Test API key for testing"
        )
        
        assert request.name == "Test Key"
        assert request.description == "Test API key for testing"

    def test_name_required(self):
        """Test name field is required."""
        with pytest.raises(ValidationError):
            MCPKeyCreate(description="Test description")

    def test_optional_description(self):
        """Test description field is optional."""
        request = MCPKeyCreate(name="Test Key")
        assert request.name == "Test Key"
        assert request.description is None


class TestMCPKeyRead:
    """Test MCPKeyRead schema validation."""

    def test_valid_key_read(self):
        """Test valid API key read response."""
        response = MCPKeyRead(
            id=1,
            name="Test Key",
            api_key="sk-test-key-123456",
            description="Test API key",
            created_at="2023-01-01T00:00:00Z",
            is_active=True
        )
        
        assert response.id == 1
        assert response.name == "Test Key"
        assert response.api_key == "sk-test-key-123456"
        assert response.is_active is True


class TestProxyToolCall:
    """Test ProxyToolCall schema validation."""

    def test_valid_tool_call(self):
        """Test valid tool call."""
        call = ProxyToolCall(
            tool_name="semantic_search",
            arguments={"query": "test", "limit": 10}
        )
        
        assert call.tool_name == "semantic_search"
        assert call.arguments == {"query": "test", "limit": 10}

    def test_tool_name_required(self):
        """Test tool_name is required."""
        with pytest.raises(ValidationError):
            ProxyToolCall(arguments={"query": "test"})

    def test_optional_arguments(self):
        """Test arguments field is optional."""
        call = ProxyToolCall(tool_name="test_tool")
        assert call.tool_name == "test_tool"
        assert call.arguments is None


class TestProxyResult:
    """Test ProxyResult schema validation."""

    def test_valid_result(self):
        """Test valid proxy result."""
        result = ProxyResult(
            status="success",
            data={"results": []},
            confidence="High",
            source="OpenSearch"
        )
        
        assert result.status == "success"
        assert result.data == {"results": []}
        assert result.confidence == "High"
        assert result.source == "OpenSearch"

    def test_status_required(self):
        """Test status field is required."""
        with pytest.raises(ValidationError):
            ProxyResult(data={"results": []})

    def test_data_required(self):
        """Test data field is required."""
        with pytest.raises(ValidationError):
            ProxyResult(status="success")

    def test_confidence_defaults(self):
        """Test default confidence value."""
        result = ProxyResult(
            status="success",
            data={"results": []}
        )
        assert result.confidence == "General"

    def test_confidence_validation(self):
        """Test confidence field validation."""
        valid_confidences = ["Low", "Medium", "High", "General"]
        
        for confidence in valid_confidences:
            result = ProxyResult(
                status="success",
                data={"results": []},
                confidence=confidence
            )
            assert result.confidence == confidence

    def test_invalid_confidence(self):
        """Test invalid confidence value."""
        with pytest.raises(ValidationError):
            ProxyResult(
                status="success",
                data={"results": []},
                confidence="InvalidConfidence"
            )

    def test_optional_fields(self):
        """Test optional source and interpretation_note fields."""
        result = ProxyResult(
            status="success",
            data={"results": []}
        )
        
        assert result.source is None
        assert result.interpretation_note is None


class TestSchemaIntegration:
    """Test integration between different schemas."""

    def test_end_to_end_workflow(self):
        """Test complete workflow with all schemas."""
        # User creates API key
        key_create = MCPKeyCreate(name="Test Key", description="Test")
        
        # System responds with key read
        key_read = MCPKeyRead(
            id=1,
            name=key_create.name,
            api_key="sk-test-key-123456",
            description=key_create.description,
            created_at="2023-01-01T00:00:00Z",
            is_active=True
        )
        
        # User performs semantic search
        search_request = SemanticSearchRequest(
            query="machine learning",
            limit=25,
            similarity_threshold=0.8
        )
        
        # System returns proxy result
        search_result = ProxyResult(
            status="success",
            data={"patents": []},
            confidence="High",
            source="OpenSearch",
            interpretation_note="Found 25 patents matching query"
        )
        
        # All objects should be valid
        assert key_create.name == key_read.name
        assert search_result.confidence == "High"
        assert search_request.limit <= 100  # Should pass validation

    def test_invalid_workflow_sequences(self):
        """Test that invalid sequences are caught by schema validation."""
        # This should fail - network analysis requires company_name
        with pytest.raises(ValidationError):
            NetworkAnalysisRequest(analysis_options=["centrality"])

        # This should fail - invalid confidence level
        with pytest.raises(ValidationError):
            ProxyResult(
                status="success",
                data={},
                confidence="InvalidLevel"
            )