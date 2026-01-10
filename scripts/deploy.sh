#!/bin/bash

set -e

echo "🚀 Starting Patent Board deployment..."

echo "📋 Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed. Please install Docker first."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is not installed. Please install Docker Compose first."; exit 1; }

echo "✅ Docker and Docker Compose are installed"

echo "🔧 Creating environment variables..."

if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration before continuing."
    echo "📝 Edit .env file and run this script again to continue deployment."
    exit 1
fi

echo "✅ Environment file found"

source .env

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY is not set in .env file"
    echo "   Please set your OpenAI API key in .env file to enable AI features."
fi

echo "🐳 Building and starting containers..."

docker-compose -f docker-compose.yml up --build -d

echo "⏳ Waiting for services to be healthy..."

for i in {1..30}; do
    if curl -f http://localhost:8001/health >/dev/null 2>&1; then
        echo "✅ Patent Board is healthy and ready!"
        echo "🌐 Web Interface: http://localhost:8001"
        echo "📚 API Documentation: http://localhost:8001/docs"
        echo "📊 Analytics Dashboard: http://localhost:8001/analytics"
        echo "⚙️  Admin Panel: http://localhost:8001/admin"
        echo "🔔 Notification Center: WebSocket enabled"
        echo ""
        echo "🐳 Container management commands:"
        echo "  View logs:        docker-compose logs -f patent-board"
        echo "  Stop services:    docker-compose -f patent-board down"
        echo "  Restart services:  docker-compose -f patent-board restart"
        echo "  Update services:  docker-compose -f patent-board pull && docker-compose -f patent-board up -d --force-recreate"
        exit 0
    fi
    
    echo "⏳ Waiting for health check... ($i/30)"
    sleep 2
done

echo "❌ Failed to start Patent Board within 60 seconds"
echo "📋 Check container logs with: docker-compose logs -f patent-board"
exit 1