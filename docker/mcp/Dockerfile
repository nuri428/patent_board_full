FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

# pyproject.toml이 참조하는 README.md를 mcp 디렉토리에 배치
COPY mcp/pyproject.toml mcp/uv.lock /app/mcp/
COPY README.md /app/mcp/README.md

# venv를 /opt/mcp-venv에 설치 (볼륨 마운트 경로 밖)
ENV UV_PROJECT_ENVIRONMENT=/opt/mcp-venv
WORKDIR /app/mcp
RUN uv sync --frozen


FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# builder에서 venv 복사
COPY --from=builder /opt/mcp-venv /opt/mcp-venv

# 전체 소스 복사 (볼륨 마운트로 덮어씌워지므로 런타임에 사용)
COPY . .

# Add back_end to PYTHONPATH for shared code access
ENV PYTHONPATH=/app/back_end:/app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

WORKDIR /app/mcp

# 볼륨 마운트 밖 /opt/mcp-venv의 uvicorn 직접 실행
CMD ["/opt/mcp-venv/bin/uvicorn", "mcp_server:mcp_app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
