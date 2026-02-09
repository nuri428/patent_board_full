import asyncio
import logging
import sys
import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../mcp")))

from sqlalchemy import select
from shared.database import get_patentdb
from app.models.patent_db import PatentMaster, ForeignPatentMaster
try:
    from mcp.services.embedding_service import EmbeddingService
except ImportError:
    try:
        from services.embedding_service import EmbeddingService
    except ImportError:
        # For direct script run in mcp container
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mcp")))
        from services.embedding_service import EmbeddingService
from mcp.database import get_opensearch_client
from mcp.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_index_if_not_exists(client, index_name):
    """Create OpenSearch index with k-NN mapping"""
    exists = client.indices.exists(index=index_name)
    if not exists:
        logger.info(f"Creating index: {index_name}")
        mapping = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100
                }
            },
            "mappings": {
                "properties": {
                    "patent_id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "abstract": {"type": "text"},
                    "country": {"type": "keyword"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 1024,
                        "method": {
                            "name": "hnsw",
                            "space_type": "l2",
                            "engine": "nmslib",
                            "parameters": {
                                "ef_construction": 128,
                                "m": 16
                            }
                        }
                    },
                    "indexed_at": {"type": "date"}
                }
            }
        }
        client.indices.create(index=index_name, body=mapping)
    else:
        logger.info(f"Index {index_name} already exists")

async def index_patents():
    embedding_service = EmbeddingService()
    opensearch = await get_opensearch_client()
    index_name = f"{settings.OPENSEARCH_INDEX_PREFIX}_patents"
    
    await create_index_if_not_exists(opensearch, index_name)
    
    async for db in get_patentdb():
        # Process KR Patents
        logger.info("Fetching KR Patents...")
        result = await db.execute(select(PatentMaster))
        kr_patents = result.scalars().all()
        
        for p in kr_patents:
            try:
                # Prepare content for embedding
                content = f"Title: {p.title}\nAbstract: {p.abstract or ''}"
                if not content.strip():
                    continue
                
                logger.info(f"Indexing KR Patent: {p.application_number}")
                embeddings = await embedding_service.encode_text(content)
                
                doc = {
                    "patent_id": p.application_number,
                    "title": p.title,
                    "abstract": p.abstract,
                    "country": "KR",
                    "embedding": embeddings["dense_vector"],
                    "indexed_at": "2026-02-09T00:00:00Z" # Using current time placeholder
                }
                
                opensearch.index(index=index_name, body=doc, id=f"KR_{p.application_number}", refresh=True)
            except Exception as e:
                logger.error(f"Error indexing KR patent {p.application_number}: {e}")

        # Process Foreign Patents
        logger.info("Fetching Foreign Patents...")
        result = await db.execute(select(ForeignPatentMaster))
        foreign_patents = result.scalars().all()
        
        for p in foreign_patents:
            try:
                content = f"Title: {p.invention_name}\nAbstract: {p.abstract or ''}"
                if not content.strip():
                    continue
                
                logger.info(f"Indexing Foreign Patent: {p.document_number}")
                embeddings = await embedding_service.encode_text(content)
                
                doc = {
                    "patent_id": p.document_number,
                    "title": p.invention_name,
                    "abstract": p.abstract,
                    "country": p.country_code,
                    "embedding": embeddings["dense_vector"],
                    "indexed_at": "2026-02-09T00:00:00Z"
                }
                
                opensearch.index(index=index_name, body=doc, id=f"F_{p.document_number}", refresh=True)
            except Exception as e:
                logger.error(f"Error indexing Foreign patent {p.document_number}: {e}")

        break # Only one session needed

if __name__ == "__main__":
    asyncio.run(index_patents())
