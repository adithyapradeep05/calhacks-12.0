import os
import json
import hashlib
import time
import math
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import anthropic
import openai
import PyPDF2
import boto3
import redis
from supabase import create_client, Client

# Import managers and classifiers
from managers.cache_manager import get_cache_manager
from managers.supabase_manager import supabase_manager
from classifiers.llm_classifier import LLMClassifier
from classifiers.keyword_classifier import KeywordClassifier
from classifiers.hybrid_classifier import HybridClassifier

# Environment variables
EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "OPENAI")
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")

# Enhanced Environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET", "ragflow-mvp-docs")

# Global variables for services
redis_client = None
supabase = None
s3_client = None
claude_client = None
openai_client = None
gemini_client = None
chroma_client = None
cache_manager = None
classifier = None

# Category-specific ChromaDB collections
category_collections = {}

# Initialize Gemini (only if using Gemini)
if EMBED_PROVIDER == "GEMINI":
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_client = genai.GenerativeModel(GEMINI_EMBED_MODEL)
        print("✅ Gemini client initialized")
    else:
        print("⚠️ GOOGLE_API_KEY not found, Gemini embeddings disabled")

# Initialize OpenAI (only if using OpenAI)
if EMBED_PROVIDER == "OPENAI":
    if OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI client initialized")
    else:
        print("⚠️ OPENAI_API_KEY not found, OpenAI embeddings disabled")

# Initialize Claude
if ANTHROPIC_API_KEY:
    claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("✅ Claude client initialized")
else:
    print("⚠️ ANTHROPIC_API_KEY not found, Claude responses disabled")

# Initialize Redis
try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()
    print(f"✅ Redis connected: {REDIS_URL}")
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}")
    redis_client = None

# Initialize Supabase
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"⚠️ Supabase connection failed: {e}")
        supabase = None
else:
    print("⚠️ SUPABASE_URL or SUPABASE_KEY not found, Supabase disabled")

# Initialize S3 (or Supabase Storage)
if AWS_ACCESS_KEY and AWS_SECRET_KEY:
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        print("✅ S3 client initialized")
    except Exception as e:
        print(f"⚠️ S3 connection failed: {e}")
        s3_client = None
elif SUPABASE_URL and SUPABASE_KEY:
    try:
        # Use Supabase Storage as S3 alternative
        s3_client = supabase.storage.from_(S3_BUCKET)
        print(f"✅ Supabase Storage initialized (bucket: {S3_BUCKET})")
    except Exception as e:
        print(f"⚠️ Supabase Storage connection failed: {e}")
        s3_client = None
else:
    print("⚠️ No storage credentials found, using local storage")

# Initialize ChromaDB
try:
    chroma_client = chromadb.PersistentClient(
        path="./storage/chroma",
        settings=Settings(anonymized_telemetry=False)
    )
    print("✅ ChromaDB client initialized")
except Exception as e:
    print(f"⚠️ ChromaDB initialization failed: {e}")
    chroma_client = None

# Initialize category-specific collections
def initialize_category_collections():
    """Initialize ChromaDB collections for each category"""
    global category_collections
    categories = ["legal", "technical", "financial", "hr", "general"]
    
    for category in categories:
        try:
            collection = chroma_client.get_or_create_collection(
                name=f"documents_{category}",
                metadata={"category": category}
            )
            category_collections[category] = collection
            print(f"✅ ChromaDB collection '{category}' initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize collection '{category}': {e}")

# Initialize multi-level cache manager
try:
    cache_manager = get_cache_manager()
    print("✅ Multi-level cache manager initialized")
except Exception as e:
    print(f"⚠️ Cache manager initialization failed: {e}")
    cache_manager = None

# Initialize classifier
try:
    classifier = HybridClassifier()
    print("✅ Hybrid classifier initialized")
except Exception as e:
    print(f"⚠️ Classifier initialization failed: {e}")
    classifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting RAGFlow Enhanced Backend...")
    initialize_category_collections()
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down RAGFlow Enhanced Backend...")
    print("✅ Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="RAGFlow Enhanced Backend",
    description="Enterprise RAG system with intelligent classification and routing",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    category: str
    confidence: float
    storage_path: str

class EmbedRequest(BaseModel):
    document_id: str
    namespace: str = "default"

class EmbedResponse(BaseModel):
    message: str
    document_id: str
    chunks_processed: int
    category: str

class QueryRequest(BaseModel):
    query: str
    namespace: str = "default"
    max_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    context: List[Dict[str, Any]]
    category: str
    sources: int
    processing_time_ms: int

class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    categories: Dict[str, int]
    cache_stats: Dict[str, Any]
    classification_stats: Dict[str, Any]

# Utility functions
def create_fallback_embedding(text: str, dimension: int = 1536) -> List[float]:
    """Create a deterministic fallback embedding when API keys are not available"""
    import hashlib
    import math
    
    # Create a hash-based embedding
    text_hash = hashlib.md5(text.encode()).hexdigest()
    embedding = []
    
    # Convert hash to embedding values
    for i in range(0, len(text_hash), 2):
        hex_pair = text_hash[i:i+2]
        val = int(hex_pair, 16) / 255.0
        embedding.append(val)
    
    # Pad or truncate to desired dimension
    while len(embedding) < dimension:
        embedding.append(0.0)
    embedding = embedding[:dimension]
    
    # Normalize the embedding
    norm = math.sqrt(sum(x*x for x in embedding))
    if norm > 0:
        embedding = [x/norm for x in embedding]
    
    return embedding

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks"""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
    
    return chunks

async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts"""
    if not texts:
        return []
    
    embeddings = []
    
    for text in texts:
        if EMBED_PROVIDER == "OPENAI" and openai_client:
            try:
                response = openai_client.embeddings.create(
                    model=OPENAI_EMBED_MODEL,
                    input=text
                )
                embeddings.append(response.data[0].embedding)
            except Exception as e:
                print(f"OpenAI embedding error: {e}")
                embeddings.append(create_fallback_embedding(text))
        
        elif EMBED_PROVIDER == "GEMINI" and gemini_client:
            try:
                response = gemini_client.embed_content(
                    model=GEMINI_EMBED_MODEL,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(response['embedding'])
            except Exception as e:
                print(f"Gemini embedding error: {e}")
                embeddings.append(create_fallback_embedding(text))
        
        else:
            # Fallback embedding
            embeddings.append(create_fallback_embedding(text))
    
    return embeddings

def log_request(endpoint: str, processing_time_ms: int, namespace: str, **kwargs):
    """Log request to Supabase"""
    if not supabase:
        return
    
    try:
        data = {
            "endpoint": endpoint,
            "processing_time_ms": processing_time_ms,
            "namespace": namespace,
            "timestamp": time.time(),
            **kwargs
        }
        supabase.table("request_logs").insert(data).execute()
    except Exception as e:
        print(f"Failed to log request: {e}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "RAGFlow Enhanced Backend v2.0.0", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "redis": "✅" if redis_client else "❌",
            "supabase": "✅" if supabase else "❌",
            "s3": "✅" if s3_client else "❌",
            "chromadb": "✅" if chroma_client else "❌",
            "claude": "✅" if claude_client else "❌",
            "cache": "✅" if cache_manager else "❌",
            "classifier": "✅" if classifier else "❌"
        }
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_file_enhanced(file: UploadFile = File(...)):
    """Enhanced file upload with automatic classification"""
    start_time = time.time()
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Read file content
    content = await file.read()
    
    # Extract text based on file type
    if file.filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(content)
    else:
        text = content.decode('utf-8', errors='ignore')
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text content found in file")
    
    # Classify document
    category = "general"
    confidence = 0.0
    reasoning = ""
    
    if classifier:
        try:
            result = await classifier.classify(text, file.filename)
            category = result.category
            confidence = result.confidence
            reasoning = getattr(result, 'reasoning', '')
        except Exception as e:
            print(f"Classification error: {e}")
            category = "general"
            confidence = 0.0
    
    # Store file in storage
    storage_path = f"{category}/{document_id}_{file.filename}"
    
    if s3_client:
        try:
            if hasattr(s3_client, 'upload'):  # Supabase Storage
                s3_client.upload(file=content, path=storage_path, file_options={"upsert": True})
            else:  # AWS S3
                s3_client.put_object(Bucket=S3_BUCKET, Key=storage_path, Body=content)
        except Exception as e:
            print(f"Storage upload error: {e}")
            # Fallback to local storage
            os.makedirs(f"./storage/uploads/{category}", exist_ok=True)
            with open(f"./storage/uploads/{storage_path}", "wb") as f:
                f.write(content)
            storage_path = f"./storage/uploads/{storage_path}"
    else:
        # Local storage fallback
        os.makedirs(f"./storage/uploads/{category}", exist_ok=True)
        with open(f"./storage/uploads/{storage_path}", "wb") as f:
            f.write(content)
        storage_path = f"./storage/uploads/{storage_path}"
    
    # Store document metadata in Supabase
    if supabase:
        try:
            supabase_manager.store_document(
                document_id=document_id,
                filename=file.filename,
                category=category,
                storage_path=storage_path,
                confidence=confidence,
                file_size=len(content),
                metadata={"reasoning": reasoning}
            )
        except Exception as e:
            print(f"Failed to store document metadata: {e}")
    
    processing_time = int((time.time() - start_time) * 1000)
    log_request("POST /upload", processing_time, "default", 
               category=category, confidence=confidence)
    
    return UploadResponse(
        message="File uploaded and classified successfully",
        document_id=document_id,
        filename=file.filename,
        category=category,
        confidence=confidence,
        storage_path=storage_path
    )

@app.post("/embed", response_model=EmbedResponse)
async def embed_document_enhanced(request: EmbedRequest):
    """Enhanced document embedding with category-specific storage"""
    start_time = time.time()
    
    if not chroma_client:
        raise HTTPException(status_code=500, detail="ChromaDB not available")
    
    # Get document from storage
    document_metadata = None
    if supabase:
        try:
            document_metadata = supabase_manager.get_document(request.document_id)
        except Exception as e:
            print(f"Failed to get document metadata: {e}")
    
    if not document_metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    category = document_metadata.get("category", "general")
    storage_path = document_metadata.get("storage_path", "")
    
    # Read document content
    try:
        if storage_path.startswith("./storage/uploads/"):
            with open(storage_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif s3_client:
            if hasattr(s3_client, 'download'):  # Supabase Storage
                content = s3_client.download(storage_path)
                text = content.decode('utf-8', errors='ignore')
            else:  # AWS S3
                response = s3_client.get_object(Bucket=S3_BUCKET, Key=storage_path)
                text = response['Body'].read().decode('utf-8', errors='ignore')
        else:
            raise HTTPException(status_code=500, detail="Storage not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read document: {e}")
    
    # Chunk text
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text chunks found")
    
    # Generate embeddings
    embeddings = await embed_texts(chunks)
    
    # Store in category-specific collection
    collection = category_collections.get(category)
    if not collection:
        raise HTTPException(status_code=500, detail=f"Collection for category '{category}' not found")
    
    # Prepare data for ChromaDB
    chunk_ids = [f"{request.document_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "document_id": request.document_id,
            "chunk_index": i,
            "category": category,
            "filename": document_metadata.get("filename", ""),
            "namespace": request.namespace
        }
        for i in range(len(chunks))
    ]
    
    # Add to collection
    try:
        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to collection: {e}")
    
    # Store embedding metadata
    if supabase:
        try:
            supabase_manager.store_embedding_metadata(
                document_id=request.document_id,
                chunk_count=len(chunks),
                embedding_model=OPENAI_EMBED_MODEL if EMBED_PROVIDER == "OPENAI" else GEMINI_EMBED_MODEL,
                processing_time=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            print(f"Failed to store embedding metadata: {e}")
    
    processing_time = int((time.time() - start_time) * 1000)
    log_request("POST /embed", processing_time, request.namespace, 
               category=category, chunks=len(chunks))
    
    return EmbedResponse(
        message="Document embedded successfully",
        document_id=request.document_id,
        chunks_processed=len(chunks),
        category=category
    )

@app.post("/query", response_model=QueryResponse)
async def query_documents_enhanced(request: QueryRequest):
    """Enhanced query with intelligent category routing and caching"""
    start_time = time.time()
    
    # Check multi-level cache first
    cache_key = f"query:{hashlib.md5(request.query.encode()).hexdigest()}"
    if cache_manager:
        cached_result, cache_level = await cache_manager.get(cache_key)
        if cached_result:
            print(f"🎯 Cache hit for query (Level: {cache_level})")
            return cached_result
    
    # Classify query to determine relevant categories
    query_category = "general"
    if classifier:
        try:
            result = await classifier.classify(request.query, "")
            query_category = result.category
        except Exception as e:
            print(f"Query classification error: {e}")
    
    # Search in relevant collections
    all_results = []
    
    # Search in primary category collection
    if query_category in category_collections:
        try:
            collection = category_collections[query_category]
            results = collection.query(
                query_texts=[request.query],
                n_results=request.max_results,
                where={"namespace": request.namespace}
            )
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    all_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0.0,
                        "category": query_category
                    })
        except Exception as e:
            print(f"Error querying {query_category} collection: {e}")
    
    # If no results in primary category, search in general collection
    if not all_results and "general" in category_collections:
        try:
            collection = category_collections["general"]
            results = collection.query(
                query_texts=[request.query],
                n_results=request.max_results,
                where={"namespace": request.namespace}
            )
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    all_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0.0,
                        "category": "general"
                    })
        except Exception as e:
            print(f"Error querying general collection: {e}")
    
    # Generate answer using Claude
    answer = "I couldn't find relevant information to answer your question."
    
    if all_results and claude_client:
        try:
            context = "\n\n".join([doc["content"] for doc in all_results[:3]])
            prompt = f"""Based on the following context, please provide a helpful answer to the user's question.

Context:
{context}

Question: {request.query}

Please provide a clear, accurate answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so."""

            response = claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=500,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            answer = response.content[0].text.strip()
        except Exception as e:
            print(f"Claude response error: {e}")
            answer = "I found relevant information but couldn't generate a response."
    
    # Cache result in multi-level cache
    result = {
        "answer": answer,
        "context": all_results,
        "category": query_category,
        "sources": len(all_results),
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    if cache_manager:
        await cache_manager.set(cache_key, result, ttl=3600)
    
    log_request("POST /query", result["processing_time_ms"], request.namespace, 
               category=query_category, sources=len(all_results))
    
    return result

@app.get("/stats", response_model=StatsResponse)
async def get_stats_enhanced():
    """Enhanced statistics with category breakdown and cache metrics"""
    stats = {
        "total_documents": 0,
        "total_chunks": 0,
        "categories": {},
        "cache_stats": {},
        "classification_stats": {}
    }
    
    # Get document counts by category
    for category, collection in category_collections.items():
        try:
            count = collection.count()
            stats["categories"][category] = count
            stats["total_chunks"] += count
        except Exception as e:
            print(f"Error getting count for {category}: {e}")
            stats["categories"][category] = 0
    
    # Get document metadata from Supabase
    if supabase:
        try:
            result = supabase.table("documents").select("category").execute()
            category_counts = {}
            for doc in result.data:
                cat = doc.get("category", "general")
                category_counts[cat] = category_counts.get(cat, 0) + 1
            stats["total_documents"] = sum(category_counts.values())
        except Exception as e:
            print(f"Error getting document stats: {e}")
    
    # Get cache statistics
    if cache_manager:
        try:
            stats["cache_stats"] = cache_manager.get_stats()
        except Exception as e:
            print(f"Error getting cache stats: {e}")
    
    # Get classification statistics
    if supabase:
        try:
            category_stats = supabase_manager.get_category_stats()
            stats["classification_stats"] = category_stats
        except Exception as e:
            print(f"Error getting classification stats: {e}")
    
    return stats

# Cache statistics endpoint
@app.get("/cache/stats")
async def cache_stats():
    """Get multi-level cache statistics"""
    if not cache_manager:
        return {"error": "Cache manager not initialized"}
    
    stats = cache_manager.get_stats()
    health = cache_manager.health_check()
    
    return {
        "cache_statistics": stats,
        "health_status": health,
        "timestamp": time.time()
    }

# Classification endpoint
@app.post("/classify")
async def classify_document(text: str, filename: str = ""):
    """Classify a document using the hybrid classifier"""
    if not classifier:
        raise HTTPException(status_code=500, detail="Classifier not available")
    
    try:
        result = await classifier.classify(text, filename)
        return {
            "category": result.category,
            "confidence": result.confidence,
            "reasoning": getattr(result, 'reasoning', ''),
            "processing_time_ms": getattr(result, 'processing_time_ms', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
