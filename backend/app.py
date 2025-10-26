import os
import json
import hashlib
import time
import math
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

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

# Import cache manager
from managers.cache_manager import get_cache_manager

# Environment variables
EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "OPENAI")  # Default to OpenAI
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))  # Smaller chunks for better retrieval
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))  # More overlap for context
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")

# Enhanced MVP Environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET", "ragflow-mvp-docs")

# Initialize Gemini (only if using Gemini)
if EMBED_PROVIDER == "GEMINI":
    if not GOOGLE_API_KEY:
        print("⚠️ GOOGLE_API_KEY not set, using fallback embedding")
    else:
        genai.configure(api_key=GOOGLE_API_KEY)

# Initialize OpenAI (only if using OpenAI)
if EMBED_PROVIDER == "OPENAI":
    if not OPENAI_API_KEY:
        print("⚠️ OPENAI_API_KEY not set, using fallback embedding")
        openai.api_key = "dummy-key"  # Will use fallback
    else:
        openai.api_key = OPENAI_API_KEY

# Initialize Claude
claude_client = None
if ANTHROPIC_API_KEY:
    claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Initialize enhanced services
try:
    redis_client = redis.from_url(REDIS_URL)
    print(f"✅ Redis connected: {REDIS_URL}")
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}")
    redis_client = None

# Initialize multi-level cache manager
try:
    cache_manager = get_cache_manager()
    print("✅ Multi-level cache manager initialized")
except Exception as e:
    print(f"⚠️ Cache manager initialization failed: {e}")
    cache_manager = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase connected")
    else:
        supabase = None
        print("⚠️ Supabase not configured")
except Exception as e:
    print(f"⚠️ Supabase connection failed: {e}")
    supabase = None

# Initialize S3 client (using Supabase Storage as fallback)
try:
    if AWS_ACCESS_KEY and AWS_SECRET_KEY:
        s3_client = boto3.client('s3', 
                                aws_access_key_id=AWS_ACCESS_KEY,
                                aws_secret_access_key=AWS_SECRET_KEY)
        print("✅ S3 client initialized")
    else:
        # Use Supabase Storage as S3 alternative
        s3_client = "supabase_storage"  # Flag for Supabase Storage usage
        print("✅ Using Supabase Storage instead of S3")
except Exception as e:
    print(f"⚠️ S3 initialization failed: {e}")
    s3_client = None

# Initialize ChromaDB with multiple collections for categories
# Initialize ChromaDB with telemetry disabled
chroma_client = chromadb.PersistentClient(
    path="./storage/chroma",
    settings=Settings(anonymized_telemetry=False)
)
collections = {
    "legal": chroma_client.get_or_create_collection("legal_docs"),
    "technical": chroma_client.get_or_create_collection("technical_docs"),
    "financial": chroma_client.get_or_create_collection("financial_docs"),
    "hr": chroma_client.get_or_create_collection("hr_docs"),
    "general": chroma_client.get_or_create_collection("general_docs")
}

# Cache directory
CACHE_DIR = Path("./storage/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "embeddings.jsonl"

# Global cache
embedding_cache = {}

# Simple category classifier for MVP
class SimpleCategoryClassifier:
    def __init__(self):
        self.keywords = {
            "legal": ["contract", "agreement", "terms", "liability", "legal", "compliance", "law", "court", "attorney"],
            "technical": ["api", "code", "implementation", "architecture", "technical", "specification", "software", "programming", "development"],
            "financial": ["budget", "cost", "revenue", "expense", "financial", "money", "accounting", "finance", "payment", "invoice"],
            "hr": ["employee", "policy", "benefits", "training", "hr", "human resources", "staff", "personnel", "workplace"]
        }
    
    def classify(self, text: str, filename: str = "") -> str:
        """Simple keyword-based classification"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        scores = {}
        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower or keyword in filename_lower)
            scores[category] = score
        
        # Return category with highest score, or 'general' if no matches
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "general"

# Simple cache manager for MVP
class SimpleCache:
    def __init__(self):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None
        try:
            result = self.redis.get(key)
            return json.loads(result) if result else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        if not self.redis:
            return
        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            print(f"Cache set error: {e}")

# Pydantic models
class UploadRequest(BaseModel):
    namespace: str = "default"

class EmbedRequest(BaseModel):
    document_id: str
    namespace: str

class QueryRequest(BaseModel):
    namespace: str
    query: str
    k: int = 4

class UploadResponse(BaseModel):
    document_id: str
    category: str
    filename: str
    storage_path: str
    processing_time_ms: int

# Lifespan event handler (replaces deprecated @app.on_event)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load cache on startup."""
    load_cache()
    print("🚀 RAGFlow MVP Enterprise Backend Started")
    print(f"📊 Categories: {list(collections.keys())}")
    yield
    # Cleanup code here if needed
    print(f"🔧 Embed Provider: {EMBED_PROVIDER}")
    print(f"💾 Redis: {'✅' if redis_client else '❌'}")
    print(f"🗄️ Supabase: {'✅' if supabase else '❌'}")
    print(f"☁️ S3: {'✅' if s3_client else '❌'}")

# Initialize FastAPI app with lifespan handler
app = FastAPI(title="RAGFlow MVP Enterprise", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
classifier = SimpleCategoryClassifier()
cache = SimpleCache()

# Utility functions (keep existing ones)
def normalize_text(s: str) -> str:
    """Normalize text by lowercasing and squeezing whitespace."""
    return re.sub(r'\s+', ' ', s.lower().strip())

def md5_hash(s: str) -> str:
    """Compute MD5 hash of a string."""
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def truncate_chunk(chunk: str, max_length: int = 6000) -> str:
    """Truncate chunk to max_length characters."""
    return chunk[:max_length]

def load_cache():
    """Load embedding cache from JSONL file."""
    global embedding_cache
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        embedding_cache[data['key']] = data['vector']
            print(f"Loaded {len(embedding_cache)} cached embeddings")
        except Exception as e:
            print(f"Error loading cache: {e}")

def cache_get(model: str, text: str) -> Optional[List[float]]:
    """Get embedding from cache."""
    key = f"{model}:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"
    return embedding_cache.get(key)

def cache_put(model: str, text: str, vector: List[float]):
    """Store embedding in cache."""
    key = f"{model}:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"
    embedding_cache[key] = vector
    
    # Append to JSONL file
    try:
        with open(CACHE_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"key": key, "vector": vector}) + '\n')
    except Exception as e:
        print(f"Error writing to cache: {e}")

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)

def extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF file."""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    # Clean the extracted text
                    page_text = ' '.join(page_text.split())  # Normalize whitespace
                    text += page_text + "\n"
            
            # Final cleanup
            text = text.strip()
            print(f"DEBUG: Extracted PDF text length: {len(text)}")
            return text
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")

def extract_pdf_text_from_bytes(content: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        import io
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                page_text = ' '.join(page_text.split())
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting PDF text from bytes: {str(e)}")

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks with better handling of small documents."""
    # Clean and normalize text
    text = text.strip()
    if not text:
        return []
    
    print(f"DEBUG: Chunking text of length: {len(text)}")
    print(f"DEBUG: Chunk size: {chunk_size}, Overlap: {chunk_overlap}")
    
    # For very small documents, return as single chunk
    if len(text) <= chunk_size:
        print(f"DEBUG: Text is small, returning as single chunk")
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Only add chunk if it has meaningful content
        if chunk.strip():
            chunks.append(chunk.strip())
            print(f"DEBUG: Created chunk {len(chunks)}: {chunk[:50]}...")
        
        if end >= len(text):
            break
            
        # Move start position, ensuring we don't go backwards
        start = max(start + chunk_size - chunk_overlap, start + 1)
    
    # Ensure we have at least one chunk
    if not chunks:
        chunks = [text]
    
    print(f"DEBUG: Created {len(chunks)} chunks total")
    return chunks

def embed_texts(texts: List[str], model: str = None) -> List[List[float]]:
    """Embed texts using configured provider (Gemini or OpenAI) with caching."""
    if model is None:
        if EMBED_PROVIDER == "OPENAI":
            model = OPENAI_EMBED_MODEL
        else:
            model = GEMINI_EMBED_MODEL
    
    embeddings = []
    batch_size = 64 if EMBED_PROVIDER == "GEMINI" else 100  # OpenAI allows larger batches
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_embeddings = []
        
        for text in batch_texts:
            # Check cache first
            cached = cache_get(model, text)
            if cached:
                batch_embeddings.append(cached)
            else:
                try:
                    if EMBED_PROVIDER == "OPENAI":
                        # Get embedding from OpenAI
                        if OPENAI_API_KEY and OPENAI_API_KEY != "dummy-key":
                            response = openai.embeddings.create(
                                model=model,
                                input=text
                            )
                            embedding = response.data[0].embedding
                        else:
                            # Use fallback embedding (simple hash-based)
                            embedding = create_fallback_embedding(text)
                    else:
                        # Get embedding from Gemini
                        if GOOGLE_API_KEY:
                            result = genai.embed_content(
                                model=model,
                                content=text,
                                task_type="retrieval_document"
                            )
                            embedding = result['embedding']
                        else:
                            # Use fallback embedding
                            embedding = create_fallback_embedding(text)
                    
                    batch_embeddings.append(embedding)
                    
                    # Cache the embedding
                    cache_put(model, text, embedding)
                except Exception as e:
                    print(f"Error embedding text with {EMBED_PROVIDER}: {e}")
                    # Use fallback embedding
                    embedding = create_fallback_embedding(text)
                    batch_embeddings.append(embedding)
        
        embeddings.extend(batch_embeddings)
    
    return embeddings

def create_fallback_embedding(text: str, dimension: int = 1536) -> List[float]:
    """Create a simple fallback embedding based on text hash"""
    import hashlib
    import math
    
    # Create a deterministic "embedding" based on text hash
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Convert hash to numbers and normalize
    embedding = []
    for i in range(0, len(text_hash), 2):
        hex_pair = text_hash[i:i+2]
        val = int(hex_pair, 16) / 255.0  # Normalize to 0-1
        embedding.append(val)
    
    # Pad or truncate to desired dimension
    while len(embedding) < dimension:
        embedding.append(0.0)
    
    embedding = embedding[:dimension]
    
    # Normalize the vector
    norm = math.sqrt(sum(x*x for x in embedding))
    if norm > 0:
        embedding = [x/norm for x in embedding]
    
    return embedding

def log_request(route: str, duration_ms: int, namespace: str, **kwargs):
    """Log request with route, duration, namespace, and counts."""
    counts = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    print(f"{route} ns={namespace} {counts} ms={duration_ms}")

# Enhanced upload endpoint with categorization
@app.post("/upload")
async def upload_file_enhanced(file: UploadFile = File(...), namespace: str = "default"):
    """Enhanced file upload with automatic categorization"""
    start_time = time.time()
    
    # Check file size (max 50MB for MVP)
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")
    
    # Read file content
    content = await file.read()
    
    # Extract text for classification
    text = ""
    if file.filename.endswith('.pdf'):
        try:
            text = extract_pdf_text_from_bytes(content)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            text = f"PDF document: {file.filename}"
    else:
        try:
            text = content.decode('utf-8')
        except Exception as e:
            print(f"Text extraction error: {e}")
            text = f"Document: {file.filename}"
    
    # Classify document
    category = classifier.classify(text, file.filename)
    print(f"📁 Document classified as: {category}")
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Store file (S3 if available, otherwise local)
    storage_path = ""
    if s3_client:
        try:
            s3_key = f"{category}/{doc_id}/{file.filename}"
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=content
            )
            storage_path = f"s3://{S3_BUCKET}/{s3_key}"
            print(f"☁️ Stored in S3: {s3_key}")
        except Exception as e:
            print(f"S3 upload error: {e}")
            # Fallback to local storage
            local_path = f"./storage/uploads/{doc_id}_{file.filename}"
            with open(local_path, "wb") as f:
                f.write(content)
            storage_path = local_path
    else:
        # Local storage fallback
        local_path = f"./storage/uploads/{doc_id}_{file.filename}"
        Path("./storage/uploads").mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(content)
        storage_path = local_path
    
    # Store metadata in Supabase if available
    if supabase:
        try:
            supabase.table("documents").insert({
                "id": doc_id,
                "filename": file.filename,
                "category": category,
                "s3_key": storage_path,
                "file_size": file.size,
                "namespace": namespace,
                "upload_time": time.time()
            }).execute()
            print(f"📊 Metadata stored in Supabase")
        except Exception as e:
            print(f"Supabase error: {e}")
    
    duration_ms = int((time.time() - start_time) * 1000)
    log_request("POST /upload", duration_ms, namespace, 
               file_size=file.size, category=category)
    
    return {
        "document_id": doc_id,
        "category": category,
        "filename": file.filename,
        "storage_path": storage_path,
        "processing_time_ms": duration_ms
    }

# Enhanced embed endpoint with category-specific storage
@app.post("/embed")
async def embed_document_enhanced(request: EmbedRequest):
    """Enhanced document embedding with category-specific storage"""
    start_time = time.time()
    
    # Handle both document_id and path formats for compatibility
    doc_id = getattr(request, 'document_id', None)
    file_path = getattr(request, 'path', None)
    
    if not doc_id and not file_path:
        raise HTTPException(status_code=400, detail="Either document_id or path is required")
    
    # Get document metadata
    doc_metadata = None
    category = "general"  # Default fallback
    storage_path = ""
    
    if doc_id and supabase:
        try:
            result = supabase.table("documents").select("*").eq("id", doc_id).execute()
            if result.data:
                doc_metadata = result.data[0]
                category = doc_metadata["category"]
                storage_path = doc_metadata["s3_key"]
        except Exception as e:
            print(f"Supabase query error: {e}")
    
    if not doc_metadata and file_path:
        # Fallback: classify based on file content
        print(f"⚠️ No metadata found, classifying file: {file_path}")
        try:
            # Read file to classify
            if file_path.endswith('.pdf'):
                text = extract_pdf_text(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Classify the document
            category = classifier.classify(text, Path(file_path).name)
            print(f"📁 Document classified as: {category}")
            storage_path = file_path
        except Exception as e:
            print(f"Error reading file for classification: {e}")
            category = "general"
            storage_path = file_path
    
    if not storage_path:
        if doc_id:
            storage_path = f"./storage/uploads/{doc_id}_*"
        else:
            raise HTTPException(status_code=400, detail="Could not determine storage path")
    
    # Download document content
    content = None
    try:
        if storage_path.startswith("s3://") and s3_client:
            # Download from S3
            bucket_key = storage_path.replace(f"s3://{S3_BUCKET}/", "")
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=bucket_key)
            content = response['Body'].read()
        else:
            # Local file
            if storage_path.startswith("./storage/uploads/"):
                # Find the actual file
                upload_dir = Path("./storage/uploads")
                for file_path in upload_dir.glob(f"{request.document_id}_*"):
                    with open(file_path, "rb") as f:
                        content = f.read()
                    break
            else:
                with open(storage_path, "rb") as f:
                    content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")
    
    if not content:
        raise HTTPException(status_code=404, detail="Document content not found")
    
    # Extract text
    if doc_metadata and doc_metadata.get("filename", "").endswith('.pdf'):
        try:
            text = extract_pdf_text_from_bytes(content)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            text = "PDF content could not be extracted"
    else:
        try:
            text = content.decode('utf-8')
        except Exception as e:
            print(f"Text extraction error: {e}")
            text = "Text content could not be extracted"
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text content extracted from document")
    
    # Chunk text
    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    
    # Generate embeddings
    embeddings = embed_texts(chunks)
    
    # Store in category-specific ChromaDB collection
    collection = collections[category]
    ids = [f"{request.document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{
        "document_id": request.document_id,
        "chunk_index": i,
        "category": category,
        "namespace": request.namespace
    } for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    duration_ms = int((time.time() - start_time) * 1000)
    log_request("POST /embed", duration_ms, request.namespace, 
               chunks=len(chunks), category=category)
    
    return {
        "chunks": len(chunks),
        "category": category,
        "processing_time_ms": duration_ms
    }

# Enhanced query endpoint with intelligent routing
@app.post("/query")
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
    
    # Simple category detection for query
    query_category = classifier.classify(request.query)
    print(f"🔍 Query classified as: {query_category}")
    
    # Generate query embedding
    query_embedding = embed_texts([request.query])[0]
    
    # Query category-specific collection
    collection = collections[query_category]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=request.k,
        where={"namespace": request.namespace},
        include=["documents", "metadatas", "distances"]
    )
    
    documents = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]
    
    if not documents:
        return {
            "answer": "No relevant documents found.",
            "context": [],
            "category": query_category,
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }
    
    # Generate answer using Claude
    context = "\n\n".join(documents)
    answer = ""
    
    if claude_client and context:
        try:
            prompt = f"""Based on the following context, answer the question: {request.query}

Context:
{context[:2000]}...

Provide a clear, concise answer based on the context. If the context doesn't contain enough information to answer the question, say so."""
            
            response = claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text
        except Exception as e:
            print(f"Claude error: {e}")
            answer = f"Based on the context: {context[:500]}..."
    else:
        answer = f"Retrieved {len(documents)} relevant documents. Context: {context[:500]}..."
    
    # Cache result in multi-level cache
    result = {
        "answer": answer,
        "context": documents,
        "category": query_category,
        "sources": len(documents),
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    if cache_manager:
        await cache_manager.set(cache_key, result, ttl=3600)
    
    log_request("POST /query", result["processing_time_ms"], request.namespace, 
               category=query_category, sources=len(documents))
    
    return result

# Enhanced stats endpoint
@app.get("/stats")
async def get_stats_enhanced():
    """Get enhanced statistics with category breakdown"""
    start_time = time.time()
    
    try:
        total_docs = 0
        by_category = {}
        by_namespace = {}
        
        # Get stats from each collection
        for category, collection in collections.items():
            try:
                count = collection.count()
                by_category[category] = count
                total_docs += count
            except Exception as e:
                print(f"Error getting count for {category}: {e}")
                by_category[category] = 0
        
        # Get namespace stats if Supabase is available
        if supabase:
            try:
                result = supabase.table("documents").select("namespace").execute()
                for doc in result.data:
                    ns = doc.get("namespace", "default")
                    by_namespace[ns] = by_namespace.get(ns, 0) + 1
            except Exception as e:
                print(f"Supabase namespace query error: {e}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "total_documents": total_docs,
            "by_category": by_category,
            "by_namespace": by_namespace,
            "collections": list(collections.keys()),
            "services": {
                "redis": "✅" if redis_client else "❌",
                "supabase": "✅" if supabase else "❌",
                "s3": "✅" if s3_client else "❌"
            },
            "processing_time_ms": duration_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

# Frontend-compatible embed endpoint
@app.post("/embed-file")
async def embed_file_by_path(request: dict):
    """Embed file by path (for frontend compatibility)"""
    start_time = time.time()
    
    file_path = request.get("path")
    namespace = request.get("namespace", "default")
    
    if not file_path:
        raise HTTPException(status_code=400, detail="Path is required")
    
    print(f"🔍 Embedding file: {file_path} in namespace: {namespace}")
    
    try:
        # Read file content
        if file_path.endswith('.pdf'):
            text = extract_pdf_text(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content extracted from document")
        
        # Classify the document
        category = classifier.classify(text, Path(file_path).name)
        print(f"📁 Document classified as: {category}")
        
        # Chunk text
        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        print(f"📄 Created {len(chunks)} chunks")
        
        # Generate embeddings
        embeddings = embed_texts(chunks)
        print(f"🧠 Generated {len(embeddings)} embeddings")
        
        # Store in correct category collection
        collection = collections[category]
        ids = [f"{namespace}_{i}_{int(time.time())}" for i in range(len(chunks))]
        metadatas = [{
            "file_path": file_path,
            "chunk_index": i,
            "category": category,
            "namespace": namespace,
            "filename": Path(file_path).name
        } for i in range(len(chunks))]
        
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Successfully stored {len(chunks)} chunks in {category} collection")
        
        duration_ms = int((time.time() - start_time) * 1000)
        log_request("POST /embed-file", duration_ms, namespace, 
                   chunks=len(chunks), category=category)
        
        return {
            "chunks": len(chunks),
            "category": category,
            "namespace": namespace,
            "processing_time_ms": duration_ms
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Clear namespace endpoint
@app.post("/clear")
async def clear_namespace_enhanced(request: dict):
    """Clear all data for a specific namespace across all categories"""
    try:
        namespace = request.get("namespace")
        if not namespace:
            raise HTTPException(status_code=400, detail="Namespace is required")
        
        cleared_count = 0
        
        # Clear from all collections
        for category, collection in collections.items():
            try:
                # Delete documents with this namespace
                collection.delete(where={"namespace": namespace})
                cleared_count += 1
            except Exception as e:
                print(f"Error clearing {category} collection: {e}")
        
        # Clear from Supabase if available
        if supabase:
            try:
                supabase.table("documents").delete().eq("namespace", namespace).execute()
            except Exception as e:
                print(f"Supabase clear error: {e}")
        
        return {
            "message": f"Cleared namespace: {namespace}",
            "collections_cleared": cleared_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing namespace: {str(e)}")

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

# Health check endpoint
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
            "chromadb": "✅",
            "claude": "✅" if claude_client else "❌",
            "cache": "✅" if cache_manager else "❌"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)