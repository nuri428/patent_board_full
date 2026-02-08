from typing import Dict, Any, List, Optional
import asyncio
import numpy as np

# from FlagEmbedding import BGEM3FlagModel
from config.settings import settings


class MockBGEM3FlagModel:
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, texts, *args, **kwargs):
        # Return dummy structure matching BGEM3FlagModel output
        if isinstance(texts, str):
            texts = [texts]

        batch_size = len(texts)
        # 1024 is typical dimension for BGE-M3
        dense_vecs = np.zeros((batch_size, 1024))
        lexical_weights = [{} for _ in range(batch_size)]
        colbert_vecs = [np.zeros((10, 1024)) for _ in range(batch_size)]

        return {
            "dense_vecs": dense_vecs,
            "lexical_weights": lexical_weights,
            "colbert_vecs": colbert_vecs,
        }


class EmbeddingService:
    _instance: Optional["EmbeddingService"] = None
    _model: Optional[MockBGEM3FlagModel] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EmbeddingService._model is None:
            self._model = MockBGEM3FlagModel(
                settings.BGE_M3_MODEL_NAME,
                use_fp16=settings.BGE_M3_USE_FP16,
                device=settings.BGE_M3_DEVICE,
            )
            EmbeddingService._model = self._model

    @property
    def model(self):
        return EmbeddingService._model

    async def encode_text(self, text: str) -> Dict[str, Any]:
        # Mock implementation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._model.encode, text, True, True, True
        )

        return {
            "dense_vector": result["dense_vecs"][0].tolist(),
            "sparse_vector": result["lexical_weights"][0],
            "colbert_vector": result.get("colbert_vecs", [])[0].tolist()
            if result.get("colbert_vecs")
            else None,
        }

    async def encode_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._model.encode, texts, True, True, True
        )

        embeddings = []
        for i in range(len(texts)):
            embeddings.append(
                {
                    "dense_vector": result["dense_vecs"][i].tolist(),
                    "sparse_vector": result["lexical_weights"][i],
                    "colbert_vector": result.get("colbert_vecs", [])[i].tolist()
                    if result.get("colbert_vecs")
                    else None,
                }
            )

        return embeddings
