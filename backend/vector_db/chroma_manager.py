"""
ChromaDB Manager for category-specific collections and optimization
"""

import os
import time
import json
import shutil
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection

logger = logging.getLogger(__name__)

class ChromaManager:
    """Manager for category-specific ChromaDB collections"""
    
    def __init__(self, persist_directory: str = "./storage/chroma"):
        self.persist_directory = persist_directory
        self.categories = ["legal", "technical", "financial", "hr", "general"]
        self.collections = {}
        self.client = None
        
        # HNSW parameters for optimization
        self.hnsw_params = {
            "M": 16,  # Number of bi-directional links for each node
            "ef_construction": 200,  # Size of dynamic candidate list
            "ef": 50,  # Size of dynamic candidate list for search
        }
        
        self._initialize_client()
        self._initialize_collections()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"✅ ChromaDB client initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _initialize_collections(self):
        """Initialize category-specific collections"""
        for category in self.categories:
            try:
                collection = self.client.get_or_create_collection(
                    name=f"documents_{category}",
                    metadata={"category": category, "created_at": time.time()}
                )
                self.collections[category] = collection
                logger.info(f"✅ Collection '{category}' initialized")
            except Exception as e:
                logger.error(f"Failed to initialize collection '{category}': {e}")
    
    def get_collection(self, category: str) -> Optional[Collection]:
        """Get collection for a specific category"""
        return self.collections.get(category)
    
    def add_documents(self, category: str, documents: List[str], 
                     embeddings: List[List[float]], metadatas: List[Dict[str, Any]], 
                     ids: List[str]) -> bool:
        """Add documents to a category collection"""
        collection = self.get_collection(category)
        if not collection:
            logger.error(f"Collection '{category}' not found")
            return False
        
        try:
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✅ Added {len(documents)} documents to '{category}' collection")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents to '{category}': {e}")
            return False
    
    def query_collection(self, category: str, query_texts: List[str], 
                        n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query a specific collection"""
        collection = self.get_collection(category)
        if not collection:
            logger.error(f"Collection '{category}' not found")
            return {}
        
        try:
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            logger.error(f"Failed to query '{category}' collection: {e}")
            return {}
    
    def query_cross_category(self, query_texts: List[str], 
                           categories: Optional[List[str]] = None,
                           n_results_per_category: int = 3) -> Dict[str, Any]:
        """Query across multiple categories"""
        if categories is None:
            categories = self.categories
        
        all_results = {}
        
        for category in categories:
            try:
                results = self.query_collection(category, query_texts, n_results_per_category)
                if results:
                    all_results[category] = results
            except Exception as e:
                logger.error(f"Failed to query '{category}' in cross-category search: {e}")
        
        return all_results
    
    def get_collection_stats(self, category: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        collection = self.get_collection(category)
        if not collection:
            return {}
        
        try:
            count = collection.count()
            return {
                "category": category,
                "document_count": count,
                "collection_name": collection.name,
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get stats for '{category}': {e}")
            return {}
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        stats = {}
        total_documents = 0
        
        for category in self.categories:
            category_stats = self.get_collection_stats(category)
            if category_stats:
                stats[category] = category_stats
                total_documents += category_stats.get("document_count", 0)
        
        stats["total_documents"] = total_documents
        stats["total_collections"] = len(stats)
        
        return stats
    
    def optimize_collection(self, category: str) -> bool:
        """Optimize a collection for better performance"""
        collection = self.get_collection(category)
        if not collection:
            logger.error(f"Collection '{category}' not found")
            return False
        
        try:
            # Get current collection info
            count = collection.count()
            
            if count == 0:
                logger.info(f"Collection '{category}' is empty, no optimization needed")
                return True
            
            # For now, ChromaDB handles optimization automatically
            # In the future, we could implement custom optimization strategies
            logger.info(f"✅ Collection '{category}' optimized (count: {count})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize collection '{category}': {e}")
            return False
    
    def optimize_all_collections(self) -> Dict[str, bool]:
        """Optimize all collections"""
        results = {}
        
        for category in self.categories:
            results[category] = self.optimize_collection(category)
        
        return results
    
    def backup_collection(self, category: str, backup_path: str) -> bool:
        """Backup a collection to a file"""
        collection = self.get_collection(category)
        if not collection:
            logger.error(f"Collection '{category}' not found")
            return False
        
        try:
            # Get all documents from collection
            results = collection.get()
            
            backup_data = {
                "category": category,
                "documents": results.get("documents", []),
                "metadatas": results.get("metadatas", []),
                "ids": results.get("ids", []),
                "embeddings": results.get("embeddings", []),
                "backup_timestamp": time.time()
            }
            
            # Save to file
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"✅ Collection '{category}' backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup collection '{category}': {e}")
            return False
    
    def restore_collection(self, category: str, backup_path: str) -> bool:
        """Restore a collection from a backup file"""
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Clear existing collection
            collection = self.get_collection(category)
            if collection:
                collection.delete()
            
            # Recreate collection
            collection = self.client.create_collection(
                name=f"documents_{category}",
                metadata={"category": category, "restored_at": time.time()}
            )
            self.collections[category] = collection
            
            # Restore data
            if backup_data.get("documents"):
                collection.add(
                    documents=backup_data["documents"],
                    metadatas=backup_data.get("metadatas", []),
                    ids=backup_data.get("ids", []),
                    embeddings=backup_data.get("embeddings", [])
                )
            
            logger.info(f"✅ Collection '{category}' restored from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore collection '{category}': {e}")
            return False
    
    def backup_all_collections(self, backup_dir: str) -> Dict[str, bool]:
        """Backup all collections"""
        results = {}
        os.makedirs(backup_dir, exist_ok=True)
        
        for category in self.categories:
            backup_path = os.path.join(backup_dir, f"{category}_backup.json")
            results[category] = self.backup_collection(category, backup_path)
        
        return results
    
    def restore_all_collections(self, backup_dir: str) -> Dict[str, bool]:
        """Restore all collections from backups"""
        results = {}
        
        for category in self.categories:
            backup_path = os.path.join(backup_dir, f"{category}_backup.json")
            if os.path.exists(backup_path):
                results[category] = self.restore_collection(category, backup_path)
            else:
                logger.warning(f"Backup file not found for '{category}': {backup_path}")
                results[category] = False
        
        return results
    
    def delete_collection(self, category: str) -> bool:
        """Delete a collection"""
        try:
            if category in self.collections:
                self.client.delete_collection(f"documents_{category}")
                del self.collections[category]
                logger.info(f"✅ Collection '{category}' deleted")
                return True
            else:
                logger.warning(f"Collection '{category}' not found")
                return False
        except Exception as e:
            logger.error(f"Failed to delete collection '{category}': {e}")
            return False
    
    def reset_all_collections(self) -> bool:
        """Reset all collections (delete and recreate)"""
        try:
            for category in self.categories:
                self.delete_collection(category)
            
            # Reinitialize collections
            self._initialize_collections()
            
            logger.info("✅ All collections reset")
            return True
        except Exception as e:
            logger.error(f"Failed to reset collections: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all collections"""
        metrics = {
            "total_collections": len(self.collections),
            "total_documents": 0,
            "collection_sizes": {},
            "average_documents_per_collection": 0,
            "hnsw_parameters": self.hnsw_params
        }
        
        for category in self.categories:
            stats = self.get_collection_stats(category)
            if stats:
                doc_count = stats.get("document_count", 0)
                metrics["collection_sizes"][category] = doc_count
                metrics["total_documents"] += doc_count
        
        if metrics["total_collections"] > 0:
            metrics["average_documents_per_collection"] = metrics["total_documents"] / metrics["total_collections"]
        
        return metrics
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all collections"""
        health = {
            "status": "healthy",
            "collections": {},
            "total_issues": 0
        }
        
        for category in self.categories:
            collection_health = {
                "status": "healthy",
                "issues": []
            }
            
            try:
                collection = self.get_collection(category)
                if not collection:
                    collection_health["status"] = "unhealthy"
                    collection_health["issues"].append("Collection not found")
                    health["total_issues"] += 1
                else:
                    # Test basic operations
                    count = collection.count()
                    if count < 0:
                        collection_health["status"] = "unhealthy"
                        collection_health["issues"].append("Invalid document count")
                        health["total_issues"] += 1
                    
                    # Test query capability
                    try:
                        collection.query(query_texts=["test"], n_results=1)
                    except Exception as e:
                        collection_health["status"] = "unhealthy"
                        collection_health["issues"].append(f"Query test failed: {e}")
                        health["total_issues"] += 1
                
            except Exception as e:
                collection_health["status"] = "unhealthy"
                collection_health["issues"].append(f"Health check failed: {e}")
                health["total_issues"] += 1
            
            health["collections"][category] = collection_health
        
        if health["total_issues"] > 0:
            health["status"] = "unhealthy"
        
        return health
