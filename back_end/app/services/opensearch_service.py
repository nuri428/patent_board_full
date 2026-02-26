"""
OpenSearch Service
외부 OpenSearch 서버에 직접 접속하여 특허 텍스트 검색 및 집계 조회를 수행합니다.
벡터 검색(시맨틱)은 MCP 서버가 담당하며, 이 서비스는 BM25 전문 검색 및 집계를 담당합니다.
"""

import logging
from typing import Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

UNIFIED_INDEX = "unified-patents-v1"
KR_INDEX = "korean_patents_sections"
US_INDEX = "us_patents_sections"


def _build_client() -> httpx.AsyncClient:
    auth = None
    if settings.OPENSEARCH_USER and settings.OPENSEARCH_PASSWORD:
        auth = (settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD)

    base_url = settings.OPENSEARCH_URL.rstrip("/")
    return httpx.AsyncClient(base_url=base_url, auth=auth, timeout=30.0)


async def search_patents_fulltext(
    query: str,
    index: str = UNIFIED_INDEX,
    limit: int = 10,
    section_types: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    BM25 전문 검색: 특허 제목/초록/청구항 등 섹션 텍스트에서 키워드 검색.

    Args:
        query: 검색어
        index: 대상 OpenSearch 인덱스
        limit: 최대 결과 수
        section_types: 특정 섹션만 검색 (예: ["TITLE", "ABSTRACT", "CLAIMS"])
    """
    must_clauses: list[dict] = [
        {
            "multi_match": {
                "query": query,
                "fields": ["section_content^2", "title^3", "abstract"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }
    ]

    if section_types:
        must_clauses.append({"terms": {"section_type": section_types}})

    body = {
        "size": limit,
        "query": {"bool": {"must": must_clauses}},
        "_source": [
            "application_number",
            "title",
            "section_type",
            "section_content",
            "ipc_codes",
            "cpc_codes",
            "country_code",
        ],
        "highlight": {
            "fields": {"section_content": {"number_of_fragments": 2, "fragment_size": 200}}
        },
    }

    async with _build_client() as client:
        response = await client.post(f"/{index}/_search", json=body)
        response.raise_for_status()
        raw = response.json()

    hits = raw.get("hits", {}).get("hits", [])
    return {
        "total": raw.get("hits", {}).get("total", {}).get("value", 0),
        "results": [
            {
                "application_number": h["_source"].get("application_number"),
                "title": h["_source"].get("title"),
                "section_type": h["_source"].get("section_type"),
                "snippet": h.get("highlight", {}).get("section_content", [""])[0],
                "ipc_codes": h["_source"].get("ipc_codes", []),
                "country_code": h["_source"].get("country_code"),
                "score": h["_score"],
            }
            for h in hits
        ],
    }


async def get_patent_sections(application_number: str) -> dict[str, Any]:
    """
    특정 출원번호의 모든 섹션을 조회합니다.
    """
    body = {
        "query": {"term": {"application_number": application_number}},
        "size": 20,
        "_source": ["section_type", "section_content", "application_number", "title"],
        "sort": [{"section_type": {"order": "asc"}}],
    }

    async with _build_client() as client:
        response = await client.post(f"/{UNIFIED_INDEX}/_search", json=body)
        response.raise_for_status()
        raw = response.json()

    hits = raw.get("hits", {}).get("hits", [])
    return {
        "application_number": application_number,
        "sections": [
            {
                "section_type": h["_source"].get("section_type"),
                "content": h["_source"].get("section_content"),
            }
            for h in hits
        ],
    }


async def get_aggregated_stats(
    index: str = UNIFIED_INDEX,
    top_n: int = 10,
) -> dict[str, Any]:
    """
    Visual Analytics용 집계 통계 조회.
    - IPC 코드 분포 (상위 N개)
    - 국가 코드 분포
    - 섹션 타입 분포
    """
    body = {
        "size": 0,
        "aggs": {
            "ipc_distribution": {
                "terms": {"field": "ipc_codes", "size": top_n}
            },
            "country_distribution": {
                "terms": {"field": "country_code", "size": 10}
            },
            "section_distribution": {
                "terms": {"field": "section_type", "size": 20}
            },
        },
    }

    async with _build_client() as client:
        response = await client.post(f"/{index}/_search", json=body)
        response.raise_for_status()
        raw = response.json()

    aggs = raw.get("aggregations", {})

    def _buckets(agg_key: str) -> list[dict]:
        return [
            {"key": b["key"], "count": b["doc_count"]}
            for b in aggs.get(agg_key, {}).get("buckets", [])
        ]

    return {
        "ipc_distribution": _buckets("ipc_distribution"),
        "country_distribution": _buckets("country_distribution"),
        "section_distribution": _buckets("section_distribution"),
    }


async def health_check() -> dict[str, Any]:
    """OpenSearch 연결 상태 확인"""
    try:
        async with _build_client() as client:
            response = await client.get("/_cluster/health")
            response.raise_for_status()
            data = response.json()
            return {"status": data.get("status", "unknown"), "connected": True}
    except Exception as e:
        logger.warning(f"OpenSearch health check failed: {e}")
        return {"status": "unreachable", "connected": False, "error": str(e)}
