# RAGFlow Setup Instructions

## Prerequisites
- Python 3.8 or higher
- Git
- API Keys (OpenAI and Anthropic)

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd calhacks-12.0
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Note**: Make sure you're in the `backend/` directory when running this command. The `requirements.txt` file is located in the `backend/` folder.

#### Set Up Environment Variables
```bash
# Copy the template and create your .env file
cp env_template.txt .env

# Edit the .env file with your actual API keys
# Replace the placeholder values with your real API keys
```

#### Get API Keys
1. **OpenAI API Key**: 
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Add it to your `.env` file

2. **Anthropic API Key**:
   - Go to https://console.anthropic.com/
   - Create a new API key
   - Add it to your `.env` file

#### Start the Backend
```bash
python run.py
```

You should see output like:
```
Starting RAGFlow Backend...
Embedding Provider: OPENAI
OpenAI API Key: Set
OpenAI Embed Model: text-embedding-3-small
Claude Model: claude-3-sonnet-20240229
ChromaDB: ./storage/chroma
Cache: ./storage/cache
Backend running on http://localhost:8000
```

### 3. Frontend Setup (Optional)

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Start the Frontend
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Testing the Backend

### Quick Health Check
```bash
# From the project root
python check_backend.py
```

### Test Complete Workflow
```bash
# From the project root
python test_complete_workflow.py
```

## API Endpoints

Once running, the backend provides these endpoints:

- `GET /stats` - Get system statistics
- `POST /upload` - Upload documents
- `POST /embed` - Embed documents into vector database
- `POST /query` - Query documents with AI
- `POST /clear` - Clear namespace data

## Troubleshooting

### Backend Won't Start
1. Check if port 8000 is available
2. Verify API keys are set in `.env`
3. Check Python version (3.8+ required)

### API Key Issues
1. Ensure keys are valid and have sufficient credits
2. Check for typos in the `.env` file
3. Restart the backend after changing keys

### ChromaDB Issues
1. Delete `./storage/chroma` folder to reset
2. Check disk space
3. Ensure write permissions

## Example Usage

### Upload and Embed a Document
```bash
# Upload
curl -F "file=@test-document.txt" http://localhost:8000/upload

# Embed (replace with actual path from upload response)
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"path": "./storage/uploads/test-document.txt", "namespace": "demo"}'
```

### Query Documents
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"namespace": "demo", "query": "What is this document about?", "k": 3}'
```

## Support

If you encounter issues:
1. Check the backend logs for error messages
2. Verify all dependencies are installed
3. Ensure API keys are valid
4. Check the troubleshooting section above
