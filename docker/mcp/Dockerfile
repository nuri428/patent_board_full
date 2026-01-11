FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY mcp/pyproject.toml .
COPY README.md .

RUN pip install --no-cache-dir uv && \
    uv sync


COPY . .

# Add back_end to PYTHONPATH for shared code access
ENV PYTHONPATH=/app/back_end:/app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uv", "run", "uvicorn", "mcp.mcp_server:mcp_app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
