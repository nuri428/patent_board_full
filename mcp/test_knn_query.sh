#!/bin/bash
# Test OpenSearch k-NN query with a simple vector

# Generate a simple test vector (1024 dimensions, all zeros except first few)
VECTOR="[0.1, 0.2, 0.3, 0.4, 0.5"
for i in {6..1024}; do
  VECTOR="$VECTOR, 0.0"
done
VECTOR="$VECTOR]"

echo "Testing k-NN query with simple vector..."

# Test 1: Basic k-NN query
curl -u admin:admin -X POST "http://192.168.0.10:9200/unified-patents-v1/_search" \
  -H 'Content-Type: application/json' \
  -d "{
  \"size\": 3,
  \"query\": {
    \"knn\": {
      \"embedding\": {
        \"vector\": $VECTOR,
        \"k\": 3
      }
    }
  }
}" | jq '.hits.total, .hits.hits | length'

echo -e "\n\nTest 2: Match all query (sanity check)..."
curl -u admin:admin -X POST "http://192.168.0.10:9200/unified-patents-v1/_search?size=1" \
  -H 'Content-Type: application/json' \
  -d '{
  "query": {
    "match_all": {}
  }
}' | jq '.hits.total, .hits.hits | length'
