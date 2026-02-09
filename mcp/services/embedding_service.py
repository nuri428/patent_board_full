from typing import Dict, Any, List, Optional
import asyncio
import numpy as np

from sentence_transformers import SentenceTransformer
from config.settings import settings


class EmbeddingService:
    _instance: Optional["EmbeddingService"] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EmbeddingService._model is None:
            self._model = SentenceTransformer(
                settings.BGE_M3_MODEL_NAME,
                device=settings.BGE_M3_DEVICE,
            )
            EmbeddingService._model = self._model

    @property
    def model(self):
        return EmbeddingService._model

    async def encode_text(self, text: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        # SentenceTransformer returns a numpy array by default
        result = await loop.run_in_executor(
            None, lambda: self._model.encode([text], convert_to_numpy=True)
        )

        return {
            "dense_vector": result[0].tolist(),
            "sparse_vector": {},  # Not supported directly by ST yet
            "colbert_vector": None,
        }

    async def encode_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: self._model.encode(texts, convert_to_numpy=True)
        )

        embeddings = []
        for i in range(len(texts)):
            embeddings.append(
                {
                    "dense_vector": result[i].tolist(),
                    "sparse_vector": {},
                    "colbert_vector": None,
                }
            )

        return embeddings
