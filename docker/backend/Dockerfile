FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY back_end/pyproject.toml .
COPY README.md .

RUN pip install --no-cache-dir uv && \
    uv sync


COPY . .

# Add back_end to PYTHONPATH so 'app' module can be imported directly
ENV PYTHONPATH=/app/back_end:/app

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
