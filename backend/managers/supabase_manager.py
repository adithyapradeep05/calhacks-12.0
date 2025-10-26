"""
Supabase Manager for RAGFlow Enhanced Backend
Handles database connections, queries, and data management
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase client not available")

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase database operations for the RAGFlow system"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.connected = False
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Supabase connection"""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase client not available")
            return
        
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                logger.warning("Supabase credentials not provided")
                return
            
            self.client = create_client(supabase_url, supabase_key)
            self.connected = True
            logger.info("✅ Supabase connection established")
            
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            self.connected = False
    
    def is_connected(self) -> bool:
        """Check if Supabase is connected"""
        return self.connected and self.client is not None
    
    # Document Operations
    def store_document(self, document_id: str, filename: str, category: str, 
                      storage_path: str, file_size: int = None, 
                      confidence: float = 0.0, namespace: str = "default",
                      metadata: Dict = None) -> bool:
        """Store document metadata in Supabase"""
        if not self.is_connected():
            logger.warning("Supabase not connected, skipping document storage")
            return False
        
        try:
            data = {
                "id": document_id,
                "filename": filename,
                "category": category,
                "storage_path": storage_path,
                "file_size": file_size,
                "confidence": confidence,
                "namespace": namespace,
                "metadata": metadata or {},
                "upload_time": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("documents").insert(data).execute()
            logger.info(f"Document {document_id} stored in Supabase")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store document {document_id}: {e}")
            return False
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """Retrieve document metadata"""
        if not self.is_connected():
            return None
        
        try:
            result = self.client.table("documents").select("*").eq("id", document_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to retrieve document {document_id}: {e}")
            return None
    
    def get_documents_by_category(self, category: str, namespace: str = "default") -> List[Dict]:
        """Get all documents in a specific category"""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table("documents").select("*").eq("category", category).eq("namespace", namespace).execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to get documents for category {category}: {e}")
            return []
    
    def get_document_category(self, document_id: str) -> Optional[str]:
        """Get the category of a specific document"""
        doc = self.get_document(document_id)
        return doc.get("category") if doc else None
    
    # Query Logging
    def log_query(self, query: str, category: str, response_time: int, 
                 cache_hit: bool = False, namespace: str = "default", 
                 user_id: str = None) -> bool:
        """Log query performance metrics"""
        if not self.is_connected():
            return False
        
        try:
            data = {
                "query": query,
                "category": category,
                "response_time": response_time,
                "cache_hit": cache_hit,
                "namespace": namespace,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("query_logs").insert(data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            return False
    
    def get_query_stats(self, category: str = None, namespace: str = "default") -> Dict:
        """Get query statistics for a category or all categories"""
        if not self.is_connected():
            return {}
        
        try:
            query = self.client.table("query_logs").select("*")
            if category:
                query = query.eq("category", category)
            if namespace:
                query = query.eq("namespace", namespace)
            
            result = query.execute()
            queries = result.data
            
            if not queries:
                return {"total_queries": 0, "avg_response_time": 0, "cache_hit_rate": 0}
            
            total_queries = len(queries)
            avg_response_time = sum(q["response_time"] for q in queries) / total_queries
            cache_hits = sum(1 for q in queries if q["cache_hit"])
            cache_hit_rate = (cache_hits / total_queries) * 100
            
            return {
                "total_queries": total_queries,
                "avg_response_time": round(avg_response_time, 2),
                "cache_hit_rate": round(cache_hit_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get query stats: {e}")
            return {}
    
    # Category Statistics
    def get_category_stats(self) -> Dict:
        """Get aggregated category statistics"""
        if not self.is_connected():
            return {}
        
        try:
            result = self.client.table("category_stats").select("*").execute()
            return {stat["category"]: stat for stat in result.data}
        except Exception as e:
            logger.error(f"Failed to get category stats: {e}")
            return {}
    
    def update_category_stats(self, category: str, doc_count: int = None, 
                           avg_response_time: float = None, total_queries: int = None,
                           cache_hit_rate: float = None) -> bool:
        """Update category statistics"""
        if not self.is_connected():
            return False
        
        try:
            data = {"last_updated": datetime.utcnow().isoformat()}
            if doc_count is not None:
                data["doc_count"] = doc_count
            if avg_response_time is not None:
                data["avg_response_time"] = avg_response_time
            if total_queries is not None:
                data["total_queries"] = total_queries
            if cache_hit_rate is not None:
                data["cache_hit_rate"] = cache_hit_rate
            
            # Use upsert with conflict resolution
            result = self.client.table("category_stats").upsert({
                "category": category,
                **data
            }, on_conflict="category").execute()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update category stats: {e}")
            return False
    
    # Embedding Metadata
    def store_embedding_metadata(self, document_id: str, chunk_count: int, 
                               embedding_model: str = None, processing_time: int = None) -> bool:
        """Store embedding generation metadata"""
        if not self.is_connected():
            return False
        
        try:
            data = {
                "document_id": document_id,
                "chunk_count": chunk_count,
                "embedding_model": embedding_model,
                "processing_time": processing_time,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("embedding_metadata").insert(data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embedding metadata: {e}")
            return False
    
    def get_embedding_metadata(self, document_id: str) -> Optional[Dict]:
        """Get embedding metadata for a document"""
        if not self.is_connected():
            return None
        
        try:
            result = self.client.table("embedding_metadata").select("*").eq("document_id", document_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get embedding metadata: {e}")
            return None
    
    # Health Check
    def health_check(self) -> Dict:
        """Check Supabase connection health"""
        if not self.is_connected():
            return {"status": "disconnected", "error": "Supabase client not available"}
        
        try:
            # Try a simple query to test connection
            result = self.client.table("documents").select("id").limit(1).execute()
            return {"status": "connected", "tables_accessible": True}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # Database Schema Management
    def create_schema(self, schema_file: str = None) -> bool:
        """Create database schema from SQL file"""
        if not self.is_connected():
            logger.warning("Supabase not connected, cannot create schema")
            return False
        
        try:
            if schema_file and os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                
                # Note: Supabase doesn't support direct SQL execution via client
                # Schema should be created through Supabase dashboard or CLI
                logger.info("Schema file loaded. Please run the SQL in Supabase dashboard.")
                return True
            else:
                logger.warning("Schema file not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False

# Global instance
supabase_manager = SupabaseManager()
