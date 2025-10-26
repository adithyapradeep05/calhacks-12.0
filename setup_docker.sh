#!/bin/bash

# RAGFlow Docker Setup Script
echo "🐳 Setting up RAGFlow Docker Environment"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo ""
    echo "For macOS:"
    echo "  brew install --cask docker"
    echo "  # Or download from: https://www.docker.com/products/docker-desktop"
    echo ""
    echo "For Ubuntu/Debian:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo ""
    echo "For Windows:"
    echo "  Download Docker Desktop from: https://www.docker.com/products/docker-desktop"
    echo ""
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker is installed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p nginx/conf.d
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p backend/storage/{chroma,uploads,cache}

# Set permissions
chmod +x setup_docker.sh

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# RAGFlow Environment Variables
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
SUPABASE_URL=https://joszwyxywxdiwscmsyud.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impvc3p3eXh5d3hkaXdzY21zeXVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0Mjc0MjYsImV4cCI6MjA3NzAwMzQyNn0.mmGQgV4UMVG6huF-GG6p3_oJral9c4IBm9e1-s5eE3M
REDIS_URL=redis://redis:6379
EMBED_PROVIDER=OPENAI
CHUNK_SIZE=400
CHUNK_OVERLAP=100
EOF
    echo "⚠️  Please edit .env file with your actual API keys"
fi

# Validate docker-compose.yml
echo "🔍 Validating docker-compose.yml..."
if docker compose config > /dev/null 2>&1; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has errors:"
    docker compose config
    exit 1
fi

# Build the backend image
echo "🔨 Building backend Docker image..."
if docker compose build ragflow-backend; then
    echo "✅ Backend image built successfully"
else
    echo "❌ Failed to build backend image"
    exit 1
fi

# Start services
echo "🚀 Starting services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker compose ps

# Test health endpoints
echo "🏥 Testing health endpoints..."

# Test Redis
if docker compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis health check failed"
fi

# Test Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Test Nginx
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx is healthy"
else
    echo "❌ Nginx health check failed"
fi

echo ""
echo "🎉 Docker setup complete!"
echo ""
echo "📋 Services running:"
echo "  - Backend API: http://localhost:8000"
echo "  - Load Balancer: http://localhost"
echo "  - Redis: localhost:6379"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "🔧 Useful commands:"
echo "  docker compose ps                    # Check service status"
echo "  docker compose logs ragflow-backend  # View backend logs"
echo "  docker compose logs redis            # View Redis logs"
echo "  docker compose logs nginx            # View Nginx logs"
echo "  docker compose down                  # Stop all services"
echo "  docker compose restart ragflow-backend # Restart backend"
echo ""
echo "🧪 Test the API:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost/health"
echo ""
