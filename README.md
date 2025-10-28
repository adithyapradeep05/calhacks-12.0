# Velora - Document Processing System

A production-ready document processing system built for CalHacks 12.0 that combines vector databases with large language models for intelligent document search and question-answering.

## Project Information

**Built at CalHacks 12.0**

**Team Members:**
- Adithya Pradeep (25%) - Backend architecture, AI model integration, and system optimization
- Paul Pam (25%) - Vector database implementation, embedding systems, and performance tuning
- Dayyan Ahmed (25%) - Rate limiting systems, token management, and technical infrastructure
- Madhav Sreeraj Vinod (25%) - Frontend development, workflow visualization, and user interface

**Technical Focus:** Adithya, Paul, and Dayyan led the core technical implementation including backend systems, AI integration, database optimization, and infrastructure, while Madhav focused on frontend development and user experience.

## Technical Stack

### Backend
- **Framework:** FastAPI (Python)
- **Vector Database:** ChromaDB 0.4.15
- **LLM Provider:** OpenAI (GPT-4o-mini, text-embedding-3-small)
- **Document Processing:** PyPDF2 3.0.1
- **Token Management:** tiktoken 0.7.0+
- **Server:** Uvicorn with ASGI

### Frontend
- **Framework:** React 18.3.1 with TypeScript
- **Build Tool:** Vite 5.4.19
- **UI Components:** Radix UI, shadcn/ui
- **State Management:** Zustand 5.0.8
- **Workflow Visualization:** ReactFlow 11.11.4
- **Styling:** TailwindCSS 3.4.17

### Infrastructure
- **Caching:** JSONL-based embedding cache
- **Rate Limiting:** Token-based with in-memory tracking
- **Storage:** Local file system (uploads, ChromaDB persistence)
- **API:** RESTful endpoints with CORS support

### Key Features
- Vector-based document search with semantic similarity
- Intelligent text chunking with configurable overlap
- Content deduplication using MD5 hashing
- MMR (Maximum Marginal Relevance) reranking
- Multi-format support (PDF, TXT, Markdown)
- Real-time token usage monitoring
- Configurable rate limiting

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ (for frontend)
- OpenAI API Key
- 2GB minimum RAM
- 1GB disk space for vector database

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd calhacks-12.0
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python run.py
```

**Important**: The `requirements.txt` file is located in the `backend/` directory, so make sure you're in that folder when running `pip install -r requirements.txt`.

### 3. Frontend Setup (Optional)
```bash
cd frontend
npm install
npm run dev
```

## API Keys Required

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

Add it to `backend/.env`:
```
OPENAI_API_KEY=your_key_here
```

**Note**: Copy `.env.example` to `.env` and replace the placeholder values with your actual API keys.

## Usage

### Upload Document
```bash
curl -F "file=@document.pdf" http://localhost:8000/upload
```

### Embed Document
```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"path": "./storage/uploads/document.pdf", "namespace": "demo"}'
```

### Query Documents
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"namespace": "demo", "query": "What is this document about?", "k": 3}'
```

### Check Usage Statistics
```bash
curl http://localhost:8000/usage
```

## Rate Limiting

The system includes built-in rate limiting to control token usage and costs:

### Default Limits
- **10,000 tokens per minute**
- **50,000 tokens per hour** 
- **20 requests per minute**
- **800 tokens per completion**

### Configuration
Set these in your `.env` file:
```bash
MAX_TOKENS_PER_MINUTE=10000
MAX_TOKENS_PER_HOUR=50000
MAX_REQUESTS_PER_MINUTE=20
MAX_COMPLETION_TOKENS=800
```

### Model Options
- **gpt-3.5-turbo** (default): Best balance of cost/performance
- **gpt-4o**: Higher quality but expensive

Set in `.env`:
```bash
OPENAI_MODEL=gpt-3.5-turbo
```

### Cost Estimates
With gpt-3.5-turbo pricing (~$0.0002 per query):
- ~6 queries per minute maximum
- ~360 queries per hour
- ~$0.08/hour maximum cost

## Enterprise Scale Configuration

For production deployment with large contexts:

### Recommended Settings
```bash
MAX_TOKENS_PER_MINUTE=100000
MAX_TOKENS_PER_HOUR=2000000
MAX_REQUESTS_PER_MINUTE=200
MAX_COMPLETION_TOKENS=4000
```

### Context Scaling
- Remove hard-coded context limits for large documents
- Implement dynamic context based on available tokens
- Use Redis for distributed rate limiting across multiple servers

## Project Structure

```
calhacks-12.0/
├── backend/           # FastAPI backend
│   ├── app.py        # Main application
│   ├── run.py        # Startup script
│   ├── requirements.txt
│   ├── .env.example  # Environment template
│   └── .env          # Environment variables (not tracked)
├── frontend/         # React frontend
│   ├── src/
│   └── package.json
├── storage/          # Data storage (not tracked)
│   ├── chroma/       # ChromaDB data
│   └── cache/        # Embedding cache
└── README.md
```

## Troubleshooting

### Backend Issues
1. Check API keys in `.env` (copy from `.env.example`)
2. Verify Python version (3.8+)
3. Install dependencies: `pip install -r requirements.txt`
4. Check port 8000 is available

### Frontend Issues
1. Install Node.js dependencies: `npm install`
2. Check port 8080 is available
3. Ensure backend is running

## License

MIT License - This project was created for CalHacks 12.0.

## Contact

For questions about this project, please contact the team members listed above.
