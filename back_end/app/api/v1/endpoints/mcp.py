from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from app.api import deps
from app.models import User
import httpx
from app.core.config import settings
from app.schemas.mcp import (
    MCPKeyCreate,
    MCPKeyRead,
    MCPKeyResult,
    ProxyToolCall,
    ProxyResult,
)
from app.crud.mcp import get_mcp_crud

router = APIRouter()


@router.get("/keys", response_model=List[MCPKeyRead])
async def list_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all MCP API keys for current user.
    """
    crud = get_mcp_crud(db)
    keys = await crud.get_by_user(user_id=current_user.id)
    return keys


@router.post("/keys", response_model=MCPKeyResult)
async def generate_key(
    key_in: MCPKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a new MCP API key.
    """
    crud = get_mcp_crud(db)
    key = await crud.create(key_in=key_in, user_id=current_user.id)
    return key


@router.delete("/keys/{key_id}", response_model=bool)
async def revoke_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Revoke an MCP API key.
    """
    crud = get_mcp_crud(db)
    result = await crud.revoke(key_id=key_id, user_id=current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Key not found")
    return True


@router.post("/proxy", response_model=ProxyResult)
async def proxy_tool_call(
    tool_call: ProxyToolCall,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Proxy a tool call to the MCP server with authentication and data processing.
    """
    crud = get_mcp_crud(db)
    keys = await crud.get_by_user(user_id=current_user.id)
    if not keys:
        raise HTTPException(
            status_code=403, detail="No active MCP API Key found for user"
        )

    # Use the most recent active key
    api_key = keys[0].api_key

    async with httpx.AsyncClient() as client:
        try:
            # Pass sampling instructions if needed via headers or query (future-proof)
            response = await client.post(
                f"{settings.MCP_SERVER_URL}/tools/{tool_call.tool_name}",
                json=tool_call.arguments,
                headers={"X-API-Key": api_key, "X-Request-Source": "human-proxy"},
                timeout=30.0,
            )
            response.raise_for_status()
            raw_data = response.json()
        except httpx.HTTPStatusError as e:
            print(f"MCP Server HTTP Error: {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"MCP Server error: {e.response.text}",
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"MCP Proxy Error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to connect to MCP Server: {str(e)}"
            )

    # Post-processing: Bucketizing and Sampling
    processed_data = process_mcp_response(tool_call.tool_name, raw_data)

    return processed_data


def process_mcp_response(tool_name: str, raw_data: Any) -> ProxyResult:
    """
    Process raw MCP response: Bucketize scores and sample graph data.
    Acts as the 'Human Adapter'.
    """
    confidence = "Medium"  # Default
    interpretation_note = None
    source = "KIPRIS (via MCP)"

    # Extract data from standardized wrapper if present
    content = raw_data
    if isinstance(raw_data, dict) and "status" in raw_data and "data" in raw_data:
        content = raw_data["data"]
        source = raw_data.get("metadata", {}).get("engine", source)
        if "confidence" in raw_data.get("metadata", {}):
            confidence = raw_data["metadata"]["confidence"]

    # 1. Score-based Confidence (if not provided by MCP)
    if confidence == "Medium" and isinstance(content, dict) and "score" in content:
        score = content.get("score", 0)
        if score > 0.8:
            confidence = "High"
        elif score < 0.4:
            confidence = "Low"

    # 2. Graph Sampling (Human UI optimization)
    if "graph" in tool_name or (isinstance(content, dict) and "nodes" in content):
        if isinstance(content, dict):
            nodes = content.get("nodes", [])
            edges = content.get("edges", [])

            # Sample for UI performance
            if len(nodes) > 30:
                # Basic sampling: take the first 30 (assuming they might be ranked)
                content["nodes"] = nodes[:30]
                sampled_node_ids = {n.get("id") for n in content["nodes"]}
                content["edges"] = [
                    e
                    for e in edges
                    if e.get("from") in sampled_node_ids
                    and e.get("to") in sampled_node_ids
                ]
                interpretation_note = (
                    f"Showing top 30 nodes out of {len(nodes)} for performance."
                )
            elif len(nodes) > 0:
                interpretation_note = f"Displaying {len(nodes)} nodes."

    return ProxyResult(
        status="success",
        data=content,
        confidence=confidence,
        interpretation_note=interpretation_note,
        source=source,
    )
