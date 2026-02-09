import json

# Create a simple 1024-dimensional vector
vector = [0.1] * 1024

# Create the script_score query
query = {
    "size": 3,
    "query": {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "knn_score",
                "lang": "knn",
                "params": {
                    "field": "embedding",
                    "query_value": vector,
                    "space_type": "cosinesimil"
                }
            }
        }
    }
}

# Print the query
print(json.dumps(query))
