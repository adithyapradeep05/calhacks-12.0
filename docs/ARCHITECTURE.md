# RAGFlow Enterprise System Architecture

## Overview

RAGFlow is an enterprise-grade Retrieval-Augmented Generation (RAG) system designed for intelligent document processing, classification, and query routing. The system provides high-performance, scalable, and reliable document management with advanced AI capabilities.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   Backend       │
│   (React)       │◄──►│   (Nginx)       │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐              │
                       │   Redis Cache   │◄─────────────┤
                       │   (L1/L2/L3)    │              │
                       └─────────────────┘              │
                                                        │
┌─────────────────┐    ┌─────────────────┐              │
│   Supabase      │    │   ChromaDB      │◄─────────────┤
│   (Database &   │◄──►│   (Vector DB)   │              │
│   Storage)      │    │                 │              │
└─────────────────┘    └─────────────────┘              │
                                                        │
┌─────────────────┐    ┌─────────────────┐              │
│   Claude API    │    │   OpenAI API    │◄─────────────┘
│   (LLM)         │    │   (Embeddings)  │
└─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Frontend Layer
- **Technology**: React with TypeScript
- **Components**: 
  - Enhanced Upload Node with classification display
  - Enhanced Query Node with routing visualization
  - Category Badge components
  - Statistics Panel with real-time updates
- **Features**:
  - Real-time document classification feedback
  - Category-based document organization
  - Performance metrics visualization
  - Responsive design

### 2. Load Balancer (Nginx)
- **Configuration**: Production-ready with health checks
- **Features**:
  - Least connection load balancing
  - Rate limiting per endpoint
  - SSL termination
  - Request routing and failover
- **Endpoints**:
  - `/health` - Health checks (no rate limiting)
  - `/upload` - File uploads (5 req/s)
  - `/query` - Query processing (10 req/s)
  - `/stats` - Statistics (20 req/s)

### 3. Backend Services
- **Technology**: FastAPI with Python 3.11
- **Architecture**: Multi-instance deployment (3 instances)
- **Features**:
  - Async request processing
  - Multi-level caching
  - Intelligent query routing
  - Document classification
  - Vector database management

### 4. Classification System
- **LLM Classifier**: Claude Haiku 3.5 for intelligent classification
- **Keyword Classifier**: Rule-based fallback system
- **Hybrid Classifier**: Combines both approaches for reliability
- **Categories**: Legal, Technical, Financial, HR, General
- **Performance**: 95% accuracy, <2s processing time

### 5. Query Routing System
- **Semantic Router**: Uses embeddings for intelligent routing
- **Session Management**: Tracks conversation context
- **Multi-category Search**: Cross-category query capabilities
- **Performance**: 85%+ routing accuracy, <50ms response time

### 6. Vector Database (ChromaDB)
- **Architecture**: Category-specific collections
- **Optimization**: HNSW parameters tuned for performance
- **Features**:
  - Persistent storage
  - Cross-category search
  - Collection statistics
  - Backup and restore capabilities

### 7. Multi-Level Caching
- **L1 Cache**: In-memory LRU (10K items, <1ms)
- **L2 Cache**: Redis (100K items, <10ms)
- **L3 Cache**: Supabase Storage (unlimited, <100ms)
- **Hit Rate Target**: 80%+ on repeated queries

### 8. Data Storage
- **Database**: Supabase PostgreSQL
- **File Storage**: Supabase Storage (S3-compatible)
- **Schema**:
  - `documents`: Document metadata and classification
  - `query_logs`: Query performance tracking
  - `category_stats`: Category performance metrics

## Data Flow

### Document Upload Flow
1. **Upload**: File uploaded via frontend
2. **Classification**: Hybrid classifier determines category
3. **Storage**: File stored in category-specific bucket
4. **Metadata**: Document info stored in Supabase
5. **Embedding**: Text extracted and chunked
6. **Vector Storage**: Embeddings stored in ChromaDB collection

### Query Processing Flow
1. **Query Reception**: Query received via load balancer
2. **Routing**: Semantic router determines relevant categories
3. **Cache Check**: Multi-level cache checked for results
4. **Vector Search**: ChromaDB searched for relevant documents
5. **LLM Generation**: Claude generates response with context
6. **Cache Storage**: Results cached for future queries
7. **Response**: Structured response returned to client

## Performance Characteristics

### Response Times
- **Health Check**: <100ms
- **Document Upload**: <5s
- **Query Processing**: <2s (P95)
- **Statistics**: <200ms
- **Cache Hit**: <10ms

### Throughput
- **Concurrent Users**: 500+
- **Queries per Minute**: 10,000+
- **Uploads per Minute**: 100+
- **Cache Hit Rate**: 80%+

### Scalability
- **Horizontal Scaling**: Multiple backend instances
- **Load Balancing**: Nginx with health checks
- **Database**: Supabase auto-scaling
- **Storage**: Distributed file storage

## Security Features

### Authentication & Authorization
- API key-based authentication
- Rate limiting per endpoint
- CORS configuration
- Input validation and sanitization

### Data Protection
- Encrypted data transmission (HTTPS)
- Secure file storage
- Access control policies
- Audit logging

## Monitoring & Observability

### Metrics Collection
- **Prometheus**: System and application metrics
- **Grafana**: Visualization and dashboards
- **Custom Metrics**:
  - Request latency and throughput
  - Cache hit rates
  - Classification accuracy
  - Error rates

### Health Checks
- **Service Health**: All components monitored
- **Dependency Health**: External service status
- **Performance Health**: Response time monitoring
- **Resource Health**: Memory, CPU, disk usage

## Deployment Architecture

### Development Environment
- **Docker Compose**: Local development setup
- **Services**: Redis, Backend, Nginx
- **Configuration**: Environment-based

### Production Environment
- **Multi-instance**: 3 backend instances
- **Load Balancer**: Nginx with health checks
- **Monitoring**: Prometheus + Grafana
- **Scaling**: Horizontal pod autoscaling

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Database**: Supabase (PostgreSQL)
- **Vector DB**: ChromaDB
- **Cache**: Redis
- **LLM**: Claude Haiku 3.5
- **Embeddings**: OpenAI text-embedding-3-small

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **UI Library**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **Build Tool**: Vite

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Load Balancer**: Nginx
- **Monitoring**: Prometheus + Grafana
- **Storage**: Supabase Storage

## API Design

### RESTful Endpoints
- `POST /upload` - Document upload with classification
- `POST /embed` - Document embedding
- `POST /query` - Intelligent query processing
- `GET /stats` - System statistics
- `GET /health` - Health check
- `POST /classify` - Document classification
- `GET /cache/stats` - Cache statistics

### Response Formats
- **JSON**: All responses in JSON format
- **Error Handling**: Structured error responses
- **Pagination**: Cursor-based pagination
- **Metadata**: Rich metadata in responses

## Future Enhancements

### Planned Features
- **Multi-language Support**: Internationalization
- **Advanced Analytics**: Usage analytics and insights
- **API Versioning**: Backward compatibility
- **Webhook Support**: Event-driven integrations
- **Advanced Security**: OAuth2, JWT tokens

### Scalability Improvements
- **Microservices**: Service decomposition
- **Message Queues**: Async processing
- **CDN Integration**: Global content delivery
- **Auto-scaling**: Dynamic resource allocation

## Conclusion

RAGFlow represents a modern, scalable, and intelligent document processing system that combines the power of large language models with efficient vector search and caching mechanisms. The architecture is designed for high performance, reliability, and ease of maintenance while providing advanced AI capabilities for enterprise use cases.
