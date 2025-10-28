# RAGFlow Backend

A FastAPI backend for RAG (Retrieval-Augmented Generation) with OpenAI integration and rate limiting.

## Features

- **OpenAI Integration**: Uses GPT models for text generation and OpenAI embeddings
- **Rate Limiting**: Built-in token usage limits to control costs
- **Chunk Guards**: Truncate chunks to max 6000 characters before embedding
- **Deduplication**: Skip duplicate chunks using MD5 hashing
- **Embedding Cache**: JSONL-based cache for embeddings to avoid re-computation
- **MMR Reranking**: Optional Maximum Marginal Relevance reranking for diverse results
- **Statistics**: Collection stats with per-namespace breakdowns
- **Usage Monitoring**: Track token usage and costs
- **Logging**: Request logging with route, duration, namespace, and counts

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the server:
```bash
uvicorn app:app --reload --port 8000
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model for text generation (default: "gpt-3.5-turbo")
- `OPENAI_EMBED_MODEL`: OpenAI embedding model (default: "text-embedding-3-small")
- `MAX_TOKENS_PER_MINUTE`: Token limit per minute (default: 10000)
- `MAX_TOKENS_PER_HOUR`: Token limit per hour (default: 50000)
- `MAX_REQUESTS_PER_MINUTE`: Request limit per minute (default: 20)
- `MAX_COMPLETION_TOKENS`: Max tokens per completion (default: 800)
- `CHUNK_SIZE`: Text chunk size (default: 400)
- `CHUNK_OVERLAP`: Chunk overlap (default: 100)

### Supported Models

**OpenAI Text Generation:**
- `gpt-3.5-turbo` (default) - Best balance of cost/performance
- `gpt-4o` - Higher quality but expensive

**OpenAI Embeddings:**
- `text-embedding-3-small` (1536 dimensions) - Default
- `text-embedding-3-large` (3072 dimensions)
- `text-embedding-ada-002` (1536 dimensions)

## API Endpoints

### POST /upload
Upload a file for processing.

### POST /embed
Embed a document with chunk guards, dedup, and cache.

**Request:**
```json
{
  "path": "/path/to/file.txt",
  "namespace": "demo"
}
```

**Response:**
```json
{
  "chunks_in": 2,
  "chunks_added": 2,
  "chunks_deduped": 0,
  "namespace": "demo",
  "embedding_dim": 768,
  "ms": 1234
}
```

### POST /query
Query documents with optional MMR reranking.

**Request:**
```json
{
  "namespace": "demo",
  "query": "What does RAGFlow do?",
  "k": 4,
  "rerank": "mmr"
}
```

**Response:**
```json
{
  "context": "RAGFlow plugs docs into a vector DB...",
  "metadatas": [...],
  "ids": [...],
  "k": 4,
  "rerank": "mmr",
  "ms": 567,
  "namespace": "demo"
}
```

### GET /usage
Get current token usage statistics and cost estimates.

**Response:**
```json
{
  "minute": {
    "tokens_used": 1500,
    "tokens_remaining": 8500,
    "requests_used": 3,
    "requests_remaining": 17,
    "reset_in_seconds": 45
  },
  "hour": {
    "tokens_used": 5000,
    "tokens_remaining": 45000,
    "reset_in_seconds": 1800
  },
  "model": "gpt-3.5-turbo",
  "limits": {
    "max_tokens_per_minute": 10000,
    "max_tokens_per_hour": 50000,
    "max_requests_per_minute": 20,
    "max_completion_tokens": 800
  },
  "cost_estimate": {
    "hourly_usd": 0.003,
    "daily_usd": 0.07,
    "monthly_usd": 2.16
  }
}
```

### POST /generate
Generate a response using OpenAI (utility endpoint).

**Request:**
```json
{
  "prompt": "Explain quantum computing in simple terms"
}
```

**Response:**
```json
{
  "response": "Quantum computing uses quantum mechanical phenomena...",
  "ms": 1234,
  "tokens": 150
}
```

## Example Usage

1. **Upload files:**
```bash
echo "RAGFlow plugs docs into a vector DB and answers questions with sources." > a.txt
echo "RAGFlow uses OpenAI embeddings and GPT for generation." > b.txt

curl -s -F "file=@a.txt" http://localhost:8000/upload | tee upa.json
curl -s -F "file=@b.txt" http://localhost:8000/upload | tee upb.json
```

2. **Embed documents:**
```bash
APA=$(jq -r .path upa.json)
BPB=$(jq -r .path upb.json)

curl -s -H "Content-Type: application/json" \
  -d "{\"path\":\"$APA\",\"namespace\":\"demo\"}" \
  http://localhost:8000/embed | tee emb1.json

curl -s -H "Content-Type: application/json" \
  -d "{\"path\":\"$BPB\",\"namespace\":\"demo\"}" \
  http://localhost:8000/embed | tee emb2.json
```

3. **Query with MMR reranking:**
```bash
curl -s -H "Content-Type: application/json" \
  -d '{"namespace":"demo","query":"What does RAGFlow do?","k":4,"rerank":"mmr"}' \
  http://localhost:8000/query | jq .
```

4. **Get statistics:**
```bash
curl -s http://localhost:8000/stats | jq .
```

5. **Check usage:**
```bash
curl -s http://localhost:8000/usage | jq .
```

## Testing Checklist

- [ ] Re-embedding same file yields `chunks_added: 0` and non-zero `chunks_deduped`
- [ ] Query with `rerank: "mmr"` returns more diverse results
- [ ] Stats endpoint shows correct totals and per-namespace counts
- [ ] Usage endpoint shows token usage and cost estimates
- [ ] Rate limiting works (429 errors when limits exceeded)
- [ ] Embedding cache file `./storage/cache/embeddings.jsonl` is created
- [ ] Request logging shows route, duration, namespace, and counts
- [ ] Chunk truncation works for large inputs (6000 char limit)
- [ ] Namespace isolation works correctly
- [ ] OpenAI integration works for both query and generate endpoints
