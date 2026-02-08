# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY back_end/pyproject.toml back_end/uv.lock ./
COPY README.md .

# Install dependencies into a virtualenv
RUN uv sync --no-dev --no-install-project

# Runtime stage
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder
COPY --from=builder /app/.venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Add back_end to PYTHONPATH
ENV PYTHONPATH=/app/back_end:/app

# Default port - can be overridden by environment variable
ENV BACKEND_PORT=8001
EXPOSE ${BACKEND_PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${BACKEND_PORT}/health || exit 1

# Use shell form to allow environment variable expansion
CMD /opt/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT}
