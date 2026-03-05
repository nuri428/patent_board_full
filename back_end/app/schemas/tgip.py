from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TGIPAnalysisRequest(BaseModel):
    technology_id: str
    views: list[str] = ["RTS", "TPI", "FSS", "WSD"]


class EvidenceBundle(BaseModel):
    representativePatents: list[dict]
    ipcSignatures: list[str]
    abstractSnippets: list[str] = []
    confidenceScores: dict[str, float]


class TGIPAnalysisResponse(BaseModel):
    run_id: str
    technology_id: str
    results: dict
    evidence: EvidenceBundle
    created_at: str


class TGIPRunResponse(TGIPAnalysisResponse):
    metadata: dict = {}


class TechnologySearchResult(BaseModel):
    id: str
    name: str
    patentCount: int
    description: str = ""


class TGIPLibraryItem(BaseModel):
    run_id: str
    technology_id: str
    technology_name: str
    created_at: str
    views_computed: list[str]
