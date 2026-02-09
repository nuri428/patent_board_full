import asyncio
import sys
import os
from opensearchpy import OpenSearch

# Add current directory to path
sys.path.append(os.getcwd())

from database import opensearch_client

async def inspect_opensearch():
    print("--- Inspecting OpenSearch Index: unified-patents-v1 ---")
    try:
        # Check mapping
        mapping = opensearch_client.indices.get_mapping(index="unified-patents-v1")
        print("\n[Mapping]")
        import json
        print(json.dumps(mapping, indent=2))

        # Get doc count
        count = opensearch_client.count(index="unified-patents-v1")
        print(f"\n[Document Count]: {count['count']}")

        # Get sample docs
        sample = opensearch_client.search(index="unified-patents-v1", body={"query": {"match_all": {}}, "size": 3})
        print("\n[Sample Documents]")
        for hit in sample['hits']['hits']:
            print(f"- ID: {hit['_id']}")
            # Truncate content for display
            source = hit['_source']
            if 'content' in source:
                source['content'] = source['content'][:100] + "..."
            if 'embedding' in source:
                source['embedding'] = f"Vector of size {len(source['embedding'])}"
            print(f"  Source: {source}")

    except Exception as e:
        print(f"Error inspecting OpenSearch: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_opensearch())
