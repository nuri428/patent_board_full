#!/usr/bin/env python3
"""
Test script to verify OpenSearch k-NN query directly
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from opensearchpy import AsyncOpenSearch
from sentence_transformers import SentenceTransformer
import json


async def test_knn_search():
    # Connect to OpenSearch
    client = AsyncOpenSearch(
        hosts=[{'host': '192.168.0.10', 'port': 9200}],
        http_auth=('admin', 'admin'),
        use_ssl=False,
        verify_certs=False,
    )
    
    # Load the model
    print("Loading BGE-M3 model...")
    model = SentenceTransformer('BAAI/bge-m3', device='cpu')
    
    # Generate embedding
    query = "battery management system"
    print(f"\nGenerating embedding for: '{query}'")
    embedding = model.encode([query], convert_to_numpy=True)[0]
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding sample (first 5): {embedding[:5].tolist()}")
    
    # Test 1: Simple k-NN query
    print("\n=== Test 1: Simple k-NN query ===")
    search_body_1 = {
        "size": 3,
        "query": {
            "knn": {
                "embedding": {
                    "vector": embedding.tolist(),
                    "k": 3
                }
            }
        }
    }
    
    try:
        response_1 = await client.search(
            index='unified-patents-v1',
            body=search_body_1
        )
        print(f"Hits: {len(response_1['hits']['hits'])}")
        print(f"Total: {response_1['hits']['total']}")
        if response_1['hits']['hits']:
            print(f"Top score: {response_1['hits']['hits'][0]['_score']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: k-NN with min_score
    print("\n=== Test 2: k-NN with min_score=0.0 ===")
    search_body_2 = {
        "size": 3,
        "min_score": 0.0,
        "query": {
            "knn": {
                "embedding": {
                    "vector": embedding.tolist(),
                    "k": 3
                }
            }
        }
    }
    
    try:
        response_2 = await client.search(
            index='unified-patents-v1',
            body=search_body_2
        )
        print(f"Hits: {len(response_2['hits']['hits'])}")
        print(f"Total: {response_2['hits']['total']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Match all query to verify index access
    print("\n=== Test 3: Match all query (sanity check) ===")
    search_body_3 = {
        "size": 1,
        "query": {"match_all": {}}
    }
    
    try:
        response_3 = await client.search(
            index='unified-patents-v1',
            body=search_body_3
        )
        print(f"Hits: {len(response_3['hits']['hits'])}")
        print(f"Total: {response_3['hits']['total']}")
    except Exception as e:
        print(f"Error: {e}")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_knn_search())
