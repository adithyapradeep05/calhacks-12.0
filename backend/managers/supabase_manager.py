import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase database operations for the RAG system."""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not all([self.url, self.key]):
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required")
        
        # Use service key for admin operations, regular key for user operations
        self.client: Client = create_client(self.url, self.service_key or self.key)
        
    def insert_document(self, document_data: Dict[str, Any]) -> str:
        """Insert a new document record."""
        try:
            result = self.client.table("documents").insert(document_data).execute()
            if result.data:
                return result.data[0]["id"]
            else:
                raise Exception("No data returned from insert")
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            result = self.client.table("documents").select("*").eq("id", document_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    def get_documents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all documents in a specific category."""
        try:
            result = self.client.table("documents").select("*").eq("category", category).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting documents for category {category}: {e}")
            return []
    
    def log_query(self, query: str, categories: List[str], response_time_ms: int, 
                  cache_hit: bool = False) -> str:
        """Log a query for analytics."""
        try:
            query_data = {
                "query": query,
                "categories": categories,
                "response_time_ms": response_time_ms,
                "cache_hit": cache_hit,
                "created_at": datetime.utcnow().isoformat()
            }
            result = self.client.table("query_logs").insert(query_data).execute()
            return result.data[0]["id"] if result.data else ""
        except Exception as e:
            logger.error(f"Error logging query: {e}")
            return ""
    
    def update_category_stats(self, category: str, response_time_ms: int):
        """Update category statistics."""
        try:
            # Get current stats
            result = self.client.table("category_stats").select("*").eq("category", category).execute()
            if result.data:
                current_stats = result.data[0]
                new_avg = ((current_stats["avg_response_time_ms"] * current_stats["total_queries"]) + response_time_ms) / (current_stats["total_queries"] + 1)
                
                self.client.table("category_stats").update({
                    "avg_response_time_ms": int(new_avg),
                    "total_queries": current_stats["total_queries"] + 1
                }).eq("category", category).execute()
        except Exception as e:
            logger.error(f"Error updating category stats for {category}: {e}")
    
    def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all categories."""
        try:
            result = self.client.table("category_stats").select("*").execute()
            return {row["category"]: row for row in result.data} if result.data else {}
        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            return {}
    
    def get_recent_queries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent queries for analytics."""
        try:
            result = self.client.table("query_logs").select("*").order("created_at", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting recent queries: {e}")
            return []
    
    def get_document_count_by_category(self) -> Dict[str, int]:
        """Get document count by category."""
        try:
            result = self.client.table("documents").select("category").execute()
            counts = {}
            for row in result.data:
                category = row["category"]
                counts[category] = counts.get(category, 0) + 1
            return counts
        except Exception as e:
            logger.error(f"Error getting document counts: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Check if Supabase connection is healthy."""
        try:
            # Simple query to test connection
            result = self.client.table("category_stats").select("category").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False
