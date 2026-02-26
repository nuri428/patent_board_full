# LangGraph Chatbot Service Dockerfile
# Context-aware patent analysis chatbot with long-term memory and MCP integration

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY back_end/pyproject.toml .
COPY back_end/uv.lock .
COPY README.md .

RUN pip install --no-cache-dir uv && \
    uv sync --frozen

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Set up Python path
ENV PYTHONPATH=/app/back_end:/app:$PYTHONPATH

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["uv", "run", "--no-sync", "python", "-m", "uvicorn", "back_end.app.langgraph.chatbot.main:app", "--host", "0.0.0.0", "--port", "8001"]