import os
import time
import hashlib
import math
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class QueryRouter:
    """Semantic query router that determines which categories to search."""
    
    def __init__(self, cache_manager, embed_function):
        self.cache_manager = cache_manager
        self.embed_function = embed_function
        
        # Pre-computed category prototype embeddings
        self.category_prototypes = {
            "legal": "Contracts, agreements, legal documents, compliance, terms of service, privacy policies, legal briefs, court documents, litigation, regulatory requirements",
            "technical": "Code, programming, APIs, technical specifications, architecture documents, software documentation, technical manuals, system designs, implementation guides",
            "financial": "Invoices, budgets, financial reports, accounting documents, tax forms, expense reports, financial statements, billing, payments, transactions",
            "hr_docs": "Employee records, policies, job descriptions, benefits, employee handbooks, HR procedures, performance reviews, training materials, personnel management",
            "general": "General information, miscellaneous documents, other content that doesn't fit specific categories"
        }
        
        # Cached category embeddings
        self._category_embeddings: Dict[str, List[float]] = {}
        self._load_category_embeddings()
        
        # Routing thresholds
        self.similarity_threshold = 0.3
        self.max_categories = 3
        
        # Session management
        self.session_timeout = 3600  # 1 hour
    
    def _load_category_embeddings(self):
        """Load or compute category prototype embeddings."""
        try:
            for category, description in self.category_prototypes.items():
                # Try to get from cache first
                cache_key = f"category_prototype:{category}"
                cached_embedding = self.cache_manager.get_embedding(cache_key)
                
                if cached_embedding:
                    self._category_embeddings[category] = cached_embedding
                else:
                    # Compute and cache
                    embedding = self.embed_function([description])[0]
                    self._category_embeddings[category] = embedding
                    self.cache_manager.set_embedding(cache_key, embedding, ttl=86400)  # 24 hours
                    
            logger.info(f"Loaded {len(self._category_embeddings)} category embeddings")
            
        except Exception as e:
            logger.error(f"Error loading category embeddings: {e}")
            # Fallback to empty embeddings
            self._category_embeddings = {}
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not a or not b or len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _is_followup_query(self, query: str, session_data: Dict) -> bool:
        """Determine if this is a follow-up query based on session context."""
        if not session_data:
            return False
        
        # Simple heuristics for follow-up detection
        followup_indicators = [
            "what about", "tell me more", "explain", "how about", "also",
            "additionally", "furthermore", "moreover", "in addition",
            "can you", "could you", "please", "thanks", "thank you"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in followup_indicators)
    
    def route(self, query: str, session_id: Optional[str] = None) -> List[str]:
        """Route query to appropriate categories."""
        start_time = time.time()
        
        try:
            # Check session cache for follow-up context
            if session_id:
                session_data = self.cache_manager.get_session(session_id)
                if session_data and self._is_followup_query(query, session_data):
                    logger.info(f"Using cached routing for follow-up query: {session_data.get('categories', [])}")
                    return session_data.get('categories', ['general'])
            
            # Generate query embedding
            try:
                query_embedding = self.embed_function([query])[0]
            except Exception as e:
                logger.error(f"Error generating query embedding: {e}")
                return ['general']
            
            # Calculate similarity to category prototypes
            similarities = {}
            for category, prototype_embedding in self._category_embeddings.items():
                if prototype_embedding:
                    similarity = self._cosine_similarity(query_embedding, prototype_embedding)
                    similarities[category] = similarity
                else:
                    similarities[category] = 0.0
            
            # Sort by similarity and filter by threshold
            sorted_categories = sorted(
                similarities.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Select top categories above threshold
            selected_categories = [
                category for category, sim in sorted_categories
                if sim >= self.similarity_threshold
            ][:self.max_categories]
            
            # Fallback to general if no categories selected
            if not selected_categories:
                selected_categories = ['general']
            
            # Cache routing decision for session
            if session_id:
                session_data = {
                    'last_query': query,
                    'categories': selected_categories,
                    'timestamp': time.time(),
                    'similarities': similarities
                }
                self.cache_manager.set_session(session_id, session_data, ttl=self.session_timeout)
            
            processing_time = int((time.time() - start_time) * 1000)
            logger.info(f"Query routed to {selected_categories} in {processing_time}ms")
            
            return selected_categories
            
        except Exception as e:
            logger.error(f"Error in query routing: {e}")
            return ['general']
    
    def get_routing_stats(self, session_id: Optional[str] = None) -> Dict[str, any]:
        """Get routing statistics and debug information."""
        stats = {
            'category_embeddings_loaded': len(self._category_embeddings),
            'similarity_threshold': self.similarity_threshold,
            'max_categories': self.max_categories,
            'session_timeout': self.session_timeout
        }
        
        if session_id:
            session_data = self.cache_manager.get_session(session_id)
            if session_data:
                stats['current_session'] = {
                    'last_query': session_data.get('last_query'),
                    'categories': session_data.get('categories'),
                    'timestamp': session_data.get('timestamp'),
                    'age_seconds': time.time() - session_data.get('timestamp', 0)
                }
        
        return stats
    
    def health_check(self) -> bool:
        """Check if query router is healthy."""
        try:
            # Check if category embeddings are loaded
            if not self._category_embeddings:
                return False
            
            # Test embedding function
            test_embedding = self.embed_function(["test query"])
            if not test_embedding or not test_embedding[0]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Query router health check failed: {e}")
            return False
