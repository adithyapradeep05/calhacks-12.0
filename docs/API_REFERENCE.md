# RAGFlow API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints require authentication via API keys passed in the request headers or environment variables.

## Response Format
All responses are in JSON format with the following structure:
```json
{
  "data": {...},
  "message": "Success message",
  "status": "success"
}
```

Error responses follow this format:
```json
{
  "error": "Error message",
  "status": "error",
  "code": "ERROR_CODE"
}
```

## Endpoints

### Health Check

#### GET /health
Check system health and service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "services": {
    "redis": "✅",
    "supabase": "✅",
    "s3": "✅",
    "chromadb": "✅",
    "claude": "✅",
    "cache": "✅",
    "classifier": "✅"
  }
}
```

### Document Upload

#### POST /upload
Upload a document with automatic classification.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: File upload

**Response:**
```json
{
  "message": "File uploaded and classified successfully",
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "category": "legal",
  "confidence": 0.95,
  "storage_path": "legal/uuid-string_document.pdf"
}
```

**Error Codes:**
- `400`: No filename provided
- `400`: No text content found
- `500`: Classification failed

### Document Embedding

#### POST /embed
Generate embeddings for an uploaded document.

**Request:**
```json
{
  "document_id": "uuid-string",
  "namespace": "default"
}
```

**Response:**
```json
{
  "message": "Document embedded successfully",
  "document_id": "uuid-string",
  "chunks_processed": 15,
  "category": "legal"
}
```

**Error Codes:**
- `404`: Document not found
- `500`: Embedding generation failed

### Query Processing

#### POST /query
Process a query with intelligent routing and response generation.

**Request:**
```json
{
  "query": "What are the software license terms?",
  "namespace": "default",
  "max_results": 5
}
```

**Response:**
```json
{
  "answer": "Based on the software license agreement, the terms include...",
  "context": [
    {
      "content": "This software license agreement governs...",
      "metadata": {
        "document_id": "uuid-string",
        "chunk_index": 0,
        "category": "legal",
        "filename": "license.pdf"
      },
      "distance": 0.123,
      "category": "legal"
    }
  ],
  "category": "legal",
  "sources": 3,
  "processing_time_ms": 1250
}
```

**Error Codes:**
- `400`: Invalid query format
- `500`: Query processing failed

### System Statistics

#### GET /stats
Get comprehensive system statistics.

**Response:**
```json
{
  "total_documents": 150,
  "total_chunks": 2500,
  "categories": {
    "legal": 45,
    "technical": 38,
    "financial": 32,
    "hr": 25,
    "general": 10
  },
  "cache_stats": {
    "l1_cache": {
      "hit_rate": 0.85,
      "size": 8500,
      "max_size": 10000
    },
    "l2_cache": {
      "hit_rate": 0.72,
      "size": 45000,
      "max_size": 100000
    },
    "l3_cache": {
      "hit_rate": 0.65,
      "size": 120000,
      "max_size": -1
    }
  },
  "classification_stats": {
    "legal": {
      "doc_count": 45,
      "avg_confidence": 0.92,
      "accuracy": 0.95
    }
  }
}
```

### Document Classification

#### POST /classify
Classify a document using the hybrid classifier.

**Request:**
```json
{
  "text": "This is a software license agreement...",
  "filename": "license.pdf"
}
```

**Response:**
```json
{
  "category": "legal",
  "confidence": 0.95,
  "reasoning": "Document contains legal terms and conditions",
  "processing_time_ms": 1200
}
```

**Error Codes:**
- `400`: Invalid input
- `500`: Classification failed

### Cache Statistics

#### GET /cache/stats
Get detailed cache performance statistics.

**Response:**
```json
{
  "cache_statistics": {
    "l1_cache": {
      "hit_rate": 0.85,
      "miss_rate": 0.15,
      "size": 8500,
      "max_size": 10000,
      "evictions": 150
    },
    "l2_cache": {
      "hit_rate": 0.72,
      "miss_rate": 0.28,
      "size": 45000,
      "max_size": 100000,
      "evictions": 1200
    },
    "l3_cache": {
      "hit_rate": 0.65,
      "miss_rate": 0.35,
      "size": 120000,
      "max_size": -1,
      "evictions": 0
    }
  },
  "health_status": {
    "l1_cache": {
      "status": "healthy",
      "issues": []
    },
    "l2_cache": {
      "status": "healthy",
      "issues": []
    },
    "l3_cache": {
      "status": "healthy",
      "issues": []
    }
  },
  "timestamp": 1703123456.789
}
```

## Error Handling

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request - Invalid input
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - Service temporarily unavailable

### Error Response Format
```json
{
  "error": "Detailed error message",
  "status": "error",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes
- `INVALID_INPUT`: Invalid request parameters
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `UNSUPPORTED_FORMAT`: Unsupported file format
- `CLASSIFICATION_FAILED`: Document classification failed
- `EMBEDDING_FAILED`: Embedding generation failed
- `QUERY_FAILED`: Query processing failed
- `CACHE_ERROR`: Cache operation failed
- `DATABASE_ERROR`: Database operation failed

## Rate Limiting

### Rate Limits
- **Health Check**: No limit
- **Upload**: 5 requests/second
- **Query**: 10 requests/second
- **Stats**: 20 requests/second
- **Other endpoints**: 30 requests/second

### Rate Limit Headers
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1703123456
```

### Rate Limit Exceeded Response
```json
{
  "error": "Rate limit exceeded",
  "status": "error",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

## Request/Response Examples

### Upload Document
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

### Query Documents
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the software license terms?",
    "namespace": "default",
    "max_results": 5
  }'
```

### Get Statistics
```bash
curl -X GET http://localhost:8000/stats
```

### Classify Document
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a software license agreement...",
    "filename": "license.pdf"
  }'
```

## Webhooks (Future)

### Document Processed
```json
{
  "event": "document.processed",
  "data": {
    "document_id": "uuid-string",
    "category": "legal",
    "confidence": 0.95,
    "processing_time_ms": 1200
  },
  "timestamp": 1703123456.789
}
```

### Query Processed
```json
{
  "event": "query.processed",
  "data": {
    "query": "What are the software license terms?",
    "category": "legal",
    "sources": 3,
    "processing_time_ms": 1250
  },
  "timestamp": 1703123456.789
}
```

## SDK Examples

### Python
```python
import requests

# Upload document
with open('document.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/upload', files={'file': f})
    result = response.json()

# Query documents
response = requests.post('http://localhost:8000/query', json={
    'query': 'What are the software license terms?',
    'namespace': 'default'
})
result = response.json()
```

### JavaScript
```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/upload', {
  method: 'POST',
  body: formData
});
const result = await response.json();

// Query documents
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'What are the software license terms?',
    namespace: 'default'
  })
});
const result = await response.json();
```

## Changelog

### Version 2.0.0
- Added enhanced classification system
- Implemented multi-level caching
- Added intelligent query routing
- Enhanced API responses with metadata
- Added comprehensive statistics endpoints

### Version 1.0.0
- Initial API release
- Basic document upload and query functionality
- Simple classification system
