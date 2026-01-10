#!/bin/bash

echo "Starting Patent Board Application..."

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please update .env with your actual configuration values"
fi

echo "Starting FastAPI server on http://localhost:8001"
echo "API Documentation: http://localhost:8001/docs"
echo "Web Interface: http://localhost:8001"

uv run uvicorn app:app --host 0.0.0.0 --port 8001 --reload