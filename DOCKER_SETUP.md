# RAGFlow Docker Setup Guide

## 🐳 Docker Infrastructure Overview

This setup provides a complete enterprise RAG system with the following services:

### Core Services
- **Redis** (port 6379) - Multi-level caching
- **RAGFlow Backend** (port 8000) - FastAPI application
- **Nginx** (port 80) - Load balancer and reverse proxy

### Optional Services
- **Prometheus** (port 9090) - Metrics collection
- **Grafana** (port 3000) - Monitoring dashboards

## 📋 Prerequisites

1. **Docker & Docker Compose** installed
2. **API Keys** configured in `.env` file
3. **Supabase** credentials (already provided)

## 🚀 Quick Start

### 1. Install Docker
```bash
# macOS
brew install --cask docker

# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Windows
# Download Docker Desktop from: https://www.docker.com/products/docker-desktop
```

### 2. Configure Environment
```bash
# Copy environment template
cp backend/env_enhanced.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
SUPABASE_URL=https://joszwyxywxdiwscmsyud.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Start Services
```bash
# Run setup script
./setup_docker.sh

# Or manually
docker compose up -d
```

### 4. Verify Installation
```bash
# Check service status
docker compose ps

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost/health
```

## 📁 File Structure

```
calhacks12.0/
├── docker-compose.yml          # Main services configuration
├── .dockerignore              # Docker build exclusions
├── setup_docker.sh           # Automated setup script
├── test_docker_config.py     # Configuration validator
├── backend/
│   ├── Dockerfile            # Backend container image
│   ├── app_enhanced.py       # Enhanced FastAPI app
│   └── requirements_enhanced.txt
├── nginx/
│   └── nginx.conf            # Load balancer configuration
└── monitoring/
    ├── prometheus.yml        # Metrics configuration
    └── grafana/
        └── provisioning/
            └── datasources/
                └── prometheus.yml
```

## 🔧 Service Configuration

### Redis Service
- **Image**: redis:7-alpine
- **Port**: 6379
- **Memory**: 512MB max
- **Persistence**: Enabled with AOF
- **Health Check**: redis-cli ping

### RAGFlow Backend
- **Build**: Custom Dockerfile
- **Port**: 8000
- **Dependencies**: Redis, Supabase
- **Health Check**: /health endpoint
- **Volumes**: ./storage mounted

### Nginx Load Balancer
- **Image**: nginx:alpine
- **Port**: 80
- **Features**: 
  - Rate limiting (10 req/s API, 2 req/s uploads)
  - Gzip compression
  - Security headers
  - Health check routing

## 📊 Monitoring

### Prometheus Metrics
- **URL**: http://localhost:9090
- **Targets**: Backend, Redis
- **Scrape Interval**: 10s

### Grafana Dashboards
- **URL**: http://localhost:3000
- **Login**: admin/admin
- **Data Source**: Prometheus

## 🧪 Testing

### Configuration Test
```bash
# Validate all configuration files
python test_docker_config.py
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Load balancer health
curl http://localhost/health

# Redis health
docker compose exec redis redis-cli ping
```

### API Testing
```bash
# Upload document
curl -F "file=@test.txt" http://localhost:8000/upload

# Query documents
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"namespace": "test", "query": "What is this about?", "k": 3}'

# Get statistics
curl http://localhost:8000/stats
```

## 🔄 Development Workflow

### Start Development
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f ragflow-backend
docker compose logs -f redis
docker compose logs -f nginx
```

### Restart Services
```bash
# Restart specific service
docker compose restart ragflow-backend

# Restart all services
docker compose restart
```

### Update Code
```bash
# Rebuild backend after code changes
docker compose build ragflow-backend
docker compose up -d ragflow-backend
```

### Stop Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :6379
   lsof -i :80
   
   # Kill process or change ports in docker-compose.yml
   ```

2. **Backend Won't Start**
   ```bash
   # Check logs
   docker compose logs ragflow-backend
   
   # Check environment variables
   docker compose exec ragflow-backend env
   ```

3. **Redis Connection Failed**
   ```bash
   # Test Redis connection
   docker compose exec ragflow-backend python -c "import redis; r=redis.Redis(host='redis', port=6379); print(r.ping())"
   ```

4. **Nginx 502 Bad Gateway**
   ```bash
   # Check if backend is running
   docker compose ps ragflow-backend
   
   # Check nginx logs
   docker compose logs nginx
   ```

### Performance Tuning

1. **Increase Redis Memory**
   ```yaml
   # In docker-compose.yml
   redis:
     command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
   ```

2. **Backend Resource Limits**
   ```yaml
   # In docker-compose.yml
   ragflow-backend:
     deploy:
       resources:
         limits:
           memory: 2G
           cpus: '1.0'
   ```

3. **Nginx Worker Processes**
   ```nginx
   # In nginx/nginx.conf
   worker_processes auto;
   worker_connections 1024;
   ```

## 📈 Production Deployment

### Environment Variables
```bash
# Production .env
NODE_ENV=production
LOG_LEVEL=info
REDIS_URL=redis://redis:6379
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-production-key
```

### Security Considerations
1. Use HTTPS in production
2. Set up proper CORS policies
3. Configure rate limiting
4. Use secrets management
5. Enable firewall rules

### Scaling
```bash
# Scale backend instances
docker compose up -d --scale ragflow-backend=3

# Use external Redis cluster
# Use external database
# Use CDN for static files
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [Redis Configuration](https://redis.io/docs/management/config/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker compose logs`
2. Verify configuration: `python test_docker_config.py`
3. Test individual services
4. Check environment variables
5. Ensure all ports are available

For hackathon demo, the basic setup with Redis + Backend + Nginx is sufficient for showcasing the enterprise features!
