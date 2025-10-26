# RAGFlow - Advanced Document Processing System

RAGFlow is a cutting-edge document processing system that combines the power of vector databases with large language models to create an intelligent document search and question-answering platform.

## 🚀 Features

- **Vector-based Document Search**: Using OpenAI embeddings and ChromaDB
- **Intelligent Text Chunking**: With overlap for better context
- **Deduplication**: Prevents redundant content
- **Caching System**: For faster processing
- **MMR Reranking**: For diverse and relevant results
- **Multi-format Support**: PDF, TXT, and Markdown files
- **Real-time Chat Interface**: For document queries
- **Structured Responses**: With templates and key points

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Anthropic API Key

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd calhacks-12.0
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp env_template.txt .env
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

## 📋 API Keys Required

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Anthropic API Key**: Get from [Anthropic Console](https://console.anthropic.com/)

Add them to `backend/.env`:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## 🔧 Usage

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

## 🧪 Testing

### Quick Health Check
```bash
python check_backend.py
```

### Complete Workflow Test
```bash
python test_complete_workflow.py
```

## 📁 Project Structure

```
calhacks-12.0/
├── backend/           # FastAPI backend
│   ├── app.py        # Main application
│   ├── run.py        # Startup script
│   ├── requirements.txt
│   └── .env          # Environment variables
├── frontend/         # React frontend
│   ├── src/
│   └── package.json
├── storage/          # Data storage
│   ├── chroma/       # ChromaDB data
│   └── cache/        # Embedding cache
└── tests/           # Test scripts
```

## 🔍 Troubleshooting

### Backend Issues
1. Check API keys in `.env`
2. Verify Python version (3.8+)
3. Install dependencies: `pip install -r requirements.txt`
4. Check port 8000 is available

### Frontend Issues
1. Install Node.js dependencies: `npm install`
2. Check port 3000 is available
3. Ensure backend is running

## 📚 Documentation

- [Setup Instructions](SETUP_INSTRUCTIONS.md)
- [API Documentation](backend/README.md)
- [Frontend Guide](frontend/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the setup instructions
3. Check backend logs for errors
4. Verify API keys are valid
