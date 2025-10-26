import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection

logger = logging.getLogger(__name__)

class ChromaManager:
    """Manages multiple ChromaDB collections for different document categories."""
    
    def __init__(self, storage_path: str = "./storage/chroma"):
        self.storage_path = storage_path
        self.client = chromadb.PersistentClient(path=storage_path)
        
        # Available categories (hr renamed to hr_docs for ChromaDB compatibility)
        self.categories = ["legal", "technical", "financial", "hr_docs", "general"]
        
        # Initialize collections
        self.collections: Dict[str, Collection] = {}
        self._initialize_collections()
        
        logger.info(f"ChromaManager initialized with {len(self.collections)} collections")
    
    def _initialize_collections(self):
        """Initialize all category-specific collections."""
        for category in self.categories:
            try:
                collection = self.client.get_or_create_collection(
                    name=category,
                    metadata={
                        "hnsw:space": "cosine",
                        "description": f"Documents classified as {category}"
                    }
                )
                self.collections[category] = collection
                logger.info(f"Initialized collection: {category}")
            except Exception as e:
                logger.error(f"Failed to initialize collection {category}: {e}")
                # Create a fallback collection
                try:
                    collection = self.client.get_or_create_collection(name=category)
                    self.collections[category] = collection
                    logger.warning(f"Created fallback collection: {category}")
                except Exception as e2:
                    logger.error(f"Failed to create fallback collection {category}: {e2}")
    
    def add_document(self, category: str, chunks: List[str], 
                     embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> bool:
        """Add document chunks to a specific category collection."""
        try:
            if category not in self.collections:
                logger.error(f"Collection {category} not found")
                return False
            
            collection = self.collections[category]
            
            # Generate unique IDs for each chunk
            ids = [f"{category}:{meta.get('hash', i)}" for i, meta in enumerate(metadata)]
            
            # Add to collection
            collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadata,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to {category} collection")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to {category}: {e}")
            return False
    
    def query(self, category: str, query: str, k: int = 5, 
              include_embeddings: bool = False) -> Dict[str, Any]:
        """Query a specific category collection."""
        try:
            if category not in self.collections:
                logger.error(f"Collection {category} not found")
                return {"documents": [], "metadatas": [], "distances": [], "embeddings": []}
            
            collection = self.collections[category]
            
            # Query the collection
            result = collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"] + (["embeddings"] if include_embeddings else [])
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying {category}: {e}")
            return {"documents": [], "metadatas": [], "distances": [], "embeddings": []}
    
    def query_multi_category(self, categories: List[str], query: str, 
                           k_per_category: int = 5) -> List[Dict[str, Any]]:
        """Query multiple categories and merge results."""
        all_results = []
        
        for category in categories:
            if category in self.collections:
                try:
                    result = self.query(category, query, k_per_category)
                    
                    # Process results and add category tag
                    if result.get('documents') and result['documents'][0]:
                        for i, doc in enumerate(result['documents'][0]):
                            metadata = result['metadatas'][0][i] if result.get('metadatas') and result['metadatas'][0] else {}
                            distance = result['distances'][0][i] if result.get('distances') and result['distances'][0] else 0.0
                            
                            all_results.append({
                                'document': doc,
                                'metadata': {**metadata, 'category': category},
                                'distance': distance,
                                'category': category
                            })
                            
                except Exception as e:
                    logger.error(f"Error querying category {category}: {e}")
        
        # Sort by distance (lower is better)
        all_results.sort(key=lambda x: x['distance'])
        
        return all_results
    
    def get_collection_stats(self, category: str) -> Dict[str, Any]:
        """Get statistics for a specific collection."""
        try:
            if category not in self.collections:
                return {"error": f"Collection {category} not found"}
            
            collection = self.collections[category]
            
            # Get collection info
            count = collection.count()
            
            return {
                "category": category,
                "document_count": count,
                "collection_name": collection.name,
                "metadata": collection.metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for {category}: {e}")
            return {"error": str(e)}
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all collections."""
        stats = {}
        for category in self.categories:
            stats[category] = self.get_collection_stats(category)
        return stats
    
    def delete_documents(self, category: str, where_clause: Dict[str, Any]) -> bool:
        """Delete documents from a collection based on where clause."""
        try:
            if category not in self.collections:
                logger.error(f"Collection {category} not found")
                return False
            
            collection = self.collections[category]
            collection.delete(where=where_clause)
            
            logger.info(f"Deleted documents from {category} collection")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents from {category}: {e}")
            return False
    
    def clear_collection(self, category: str) -> bool:
        """Clear all documents from a collection."""
        try:
            if category not in self.collections:
                logger.error(f"Collection {category} not found")
                return False
            
            collection = self.collections[category]
            
            # Get all document IDs
            all_docs = collection.get()
            if all_docs['ids']:
                collection.delete(ids=all_docs['ids'])
            
            logger.info(f"Cleared {category} collection")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing {category} collection: {e}")
            return False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all collections."""
        health_status = {}
        
        for category in self.categories:
            try:
                if category in self.collections:
                    # Try to get collection count
                    count = self.collections[category].count()
                    health_status[category] = True
                else:
                    health_status[category] = False
            except Exception as e:
                logger.error(f"Health check failed for {category}: {e}")
                health_status[category] = False
        
        return health_status
