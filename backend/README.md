# RAGFlow Backend

A FastAPI backend for RAG (Retrieval-Augmented Generation) with improved indexing and retrieval quality.

## Features

- **Chunk Guards**: Truncate chunks to max 6000 characters before embedding
- **Deduplication**: Skip duplicate chunks using MD5 hashing
- **Embedding Cache**: JSONL-based cache for embeddings to avoid re-computation
- **MMR Reranking**: Optional Maximum Marginal Relevance reranking for diverse results
- **Statistics**: Collection stats with per-namespace breakdowns
- **Logging**: Request logging with route, duration, namespace, and counts

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your API keys
```

3. Run the server:
```bash
uvicorn app:app --reload --port 8000
```

### Switching Between Embedding Providers

**To use Gemini embeddings:**
```bash
EMBED_PROVIDER=GEMINI
GOOGLE_API_KEY=your_google_api_key
```

**To use OpenAI embeddings:**
```bash
EMBED_PROVIDER=OPENAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBED_MODEL=text-embedding-3-small  # or your preferred model
```

## Environment Variables

- `EMBED_PROVIDER`: Set to "GEMINI" (default) or "OPENAI"
- `GEMINI_EMBED_MODEL`: Gemini embedding model (default: "models/text-embedding-004")
- `GOOGLE_API_KEY`: Your Google API key for Gemini
- `OPENAI_API_KEY`: Your OpenAI API key (when using OpenAI embeddings)
- `OPENAI_EMBED_MODEL`: OpenAI embedding model (default: "text-embedding-3-small")
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude (optional)
- `CHUNK_SIZE`: Text chunk size (default: 800)
- `CHUNK_OVERLAP`: Chunk overlap (default: 150)

### Supported Embedding Models

**Gemini Models:**
- `models/text-embedding-004` (768 dimensions)
- `models/text-embedding-003` (768 dimensions)

**OpenAI Models:**
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

### GET /stats
Get collection statistics.

**Response:**
```json
{
  "total_vectors": 10,
  "avg_chunk_length_chars": 450,
  "by_namespace": {
    "demo": 10
  }
}
```

## Example Usage

1. **Upload files:**
```bash
echo "RAGFlow plugs docs into a vector DB and answers questions with sources." > a.txt
echo "RAGFlow uses Gemini embeddings and Claude for generation." > b.txt

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

## Testing Checklist

- [ ] Re-embedding same file yields `chunks_added: 0` and non-zero `chunks_deduped`
- [ ] Query with `rerank: "mmr"` returns more diverse results
- [ ] Stats endpoint shows correct totals and per-namespace counts
- [ ] Embedding cache file `./storage/cache/embeddings.jsonl` is created
- [ ] Request logging shows route, duration, namespace, and counts
- [ ] Chunk truncation works for large inputs (6000 char limit)
- [ ] Namespace isolation works correctly
