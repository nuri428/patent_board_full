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
COPY back_end/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for langgraph and chatbot
RUN pip install --no-cache-dir \
    langgraph \
    langgraph-checkpoint \
    langchain-openai \
    redis \
    aiomysql \
    sqlalchemy[asyncio] \
    pydantic \
    python-dotenv \
    httpx

# Copy application code
COPY back_end/ /app/back_end/
COPY shared/ /app/shared/
COPY scripts/ /app/scripts/

# Create logs directory
RUN mkdir -p /app/logs

# Set up Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["uv", "run", "python", "-m", "uvicorn", "back_end.app.langgraph.chatbot.main:app", "--host", "0.0.0.0", "--port", "8001"]