import json

# Create a simple 1024-dimensional vector
vector = [0.1] * 1024

# Create the k-NN query
query = {
    "size": 3,
    "query": {
        "knn": {
            "embedding": {
                "vector": vector,
                "k": 3
            }
        }
    }
}

# Print the query
print(json.dumps(query))
