FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    libmariadbclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY README.md .

RUN pip install --no-cache-dir uv && \
    uv sync

COPY . .

ENV PYTHONPATH=/app
ENV MARIADB_URL=mysql+aiomysql://patent_user:patent_password@db:3306/patent_db
ENV NEO4J_URI=bolt://neo4j:7687
ENV NEO4J_USER=neo4j
ENV NEO4J_PASSWORD=neo4j_password
ENV OPENAI_API_KEY=your_openai_api_key_here

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]