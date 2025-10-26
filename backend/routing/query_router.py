"""
Semantic Query Router for intelligent query routing
"""

import os
import time
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

import openai
import anthropic
from managers.cache_manager import get_cache_manager

logger = logging.getLogger(__name__)

@dataclass
class RoutingResult:
    """Result of query routing"""
    categories: List[str]
    scores: List[float]
    confidence: float
    reasoning: str
    processing_time_ms: int

class QueryRouter:
    """Intelligent query router using semantic similarity"""
    
    def __init__(self):
        self.categories = ["legal", "technical", "financial", "hr", "general"]
        self.category_embeddings = {}
        self.cache_manager = get_cache_manager()
        self.openai_client = None
        self.claude_client = None
        
        # Initialize clients
        self._init_clients()
        
        # Generate category embeddings
        self._generate_category_embeddings()
    
    def _init_clients(self):
        """Initialize OpenAI and Claude clients"""
        # OpenAI client
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)
            logger.info("✅ OpenAI client initialized for query routing")
        
        # Claude client
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.claude_client = anthropic.Anthropic(api_key=anthropic_key)
            logger.info("✅ Claude client initialized for query routing")
    
    def _generate_category_embeddings(self):
        """Generate embeddings for each category"""
        category_descriptions = {
            "legal": "Legal documents, contracts, agreements, terms of service, privacy policies, compliance, regulations, liability, court cases, legal advice",
            "technical": "Technical documentation, API references, code, software architecture, system design, programming, development, technical specifications, troubleshooting",
            "financial": "Financial reports, budgets, invoices, accounting, revenue, expenses, investments, financial analysis, cost management, financial planning",
            "hr": "Human resources, employee policies, job descriptions, training, benefits, performance reviews, workplace policies, personnel management, HR procedures",
            "general": "General information, company news, announcements, meeting notes, project updates, general communications, miscellaneous documents"
        }
        
        for category, description in category_descriptions.items():
            try:
                if self.openai_client:
                    response = self.openai_client.embeddings.create(
                        model="text-embedding-3-small",
                        input=description
                    )
                    self.category_embeddings[category] = response.data[0].embedding
                else:
                    # Fallback to simple hash-based embedding
                    self.category_embeddings[category] = self._create_fallback_embedding(description)
            except Exception as e:
                logger.error(f"Failed to generate embedding for {category}: {e}")
                self.category_embeddings[category] = self._create_fallback_embedding(description)
        
        logger.info(f"✅ Generated embeddings for {len(self.category_embeddings)} categories")
    
    def _create_fallback_embedding(self, text: str, dimension: int = 1536) -> List[float]:
        """Create a deterministic fallback embedding"""
        import hashlib
        import math
        
        text_hash = hashlib.md5(text.encode()).hexdigest()
        embedding = []
        
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            val = int(hex_pair, 16) / 255.0
            embedding.append(val)
        
        while len(embedding) < dimension:
            embedding.append(0.0)
        embedding = embedding[:dimension]
        
        norm = math.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            embedding = [x/norm for x in embedding]
        
        return embedding
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not a or not b or len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    async def route_query(self, query: str, session_id: Optional[str] = None) -> RoutingResult:
        """Route query to relevant categories"""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"routing:{hashlib.md5(query.encode()).hexdigest()}"
        if self.cache_manager:
            cached_result, cache_level = await self.cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"🎯 Cache hit for query routing (Level: {cache_level})")
                return RoutingResult(**cached_result)
        
        # Generate query embedding
        query_embedding = await self._generate_query_embedding(query)
        
        # Calculate similarities
        similarities = {}
        for category, category_embedding in self.category_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, category_embedding)
            similarities[category] = similarity
        
        # Sort by similarity
        sorted_categories = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        # Select top categories (top 2-3 with similarity > 0.3)
        top_categories = []
        top_scores = []
        
        for category, score in sorted_categories:
            if score > 0.3:  # Minimum similarity threshold
                top_categories.append(category)
                top_scores.append(score)
                if len(top_categories) >= 3:  # Maximum 3 categories
                    break
        
        # If no categories meet threshold, use top 2
        if not top_categories:
            top_categories = [cat for cat, _ in sorted_categories[:2]]
            top_scores = [score for _, score in sorted_categories[:2]]
        
        # Calculate confidence
        confidence = max(top_scores) if top_scores else 0.0
        
        # Generate reasoning
        reasoning = self._generate_routing_reasoning(query, top_categories, top_scores)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        result = RoutingResult(
            categories=top_categories,
            scores=top_scores,
            confidence=confidence,
            reasoning=reasoning,
            processing_time_ms=processing_time
        )
        
        # Cache result
        if self.cache_manager:
            await self.cache_manager.set(cache_key, result.__dict__, ttl=3600)
        
        return result
    
    async def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query"""
        try:
            if self.openai_client:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=query
                )
                return response.data[0].embedding
            else:
                return self._create_fallback_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return self._create_fallback_embedding(query)
    
    def _generate_routing_reasoning(self, query: str, categories: List[str], scores: List[float]) -> str:
        """Generate reasoning for routing decision"""
        if not categories:
            return "No relevant categories found for this query."
        
        reasoning_parts = []
        for i, (category, score) in enumerate(zip(categories, scores)):
            reasoning_parts.append(f"{category} (similarity: {score:.3f})")
        
        return f"Query routed to: {', '.join(reasoning_parts)}"
    
    async def route_with_context(self, query: str, previous_queries: List[str], session_id: str) -> RoutingResult:
        """Route query considering previous context"""
        start_time = time.time()
        
        # Check session cache
        session_cache_key = f"session_routing:{session_id}:{hashlib.md5(query.encode()).hexdigest()}"
        if self.cache_manager:
            cached_result, cache_level = await self.cache_manager.get(session_cache_key)
            if cached_result:
                logger.info(f"🎯 Session cache hit for query routing (Level: {cache_level})")
                return RoutingResult(**cached_result)
        
        # Get routing for current query
        current_routing = await self.route_query(query)
        
        # If we have previous queries, consider their context
        if previous_queries:
            # Get routing for previous queries
            previous_routings = []
            for prev_query in previous_queries[-3:]:  # Last 3 queries
                prev_routing = await self.route_query(prev_query)
                previous_routings.append(prev_routing)
            
            # Weight current routing with previous context
            context_categories = {}
            for routing in previous_routings:
                for category, score in zip(routing.categories, routing.scores):
                    context_categories[category] = context_categories.get(category, 0) + score * 0.3  # 30% weight for context
            
            # Adjust current routing with context
            adjusted_categories = []
            adjusted_scores = []
            
            for category, score in zip(current_routing.categories, current_routing.scores):
                context_boost = context_categories.get(category, 0)
                adjusted_score = score + context_boost
                adjusted_categories.append(category)
                adjusted_scores.append(adjusted_score)
            
            # Re-sort by adjusted scores
            sorted_pairs = sorted(zip(adjusted_categories, adjusted_scores), key=lambda x: x[1], reverse=True)
            current_routing.categories = [cat for cat, _ in sorted_pairs]
            current_routing.scores = [score for _, score in sorted_pairs]
            current_routing.confidence = max(current_routing.scores) if current_routing.scores else 0.0
            current_routing.reasoning += f" (context-adjusted from {len(previous_queries)} previous queries)"
        
        # Cache session result
        if self.cache_manager:
            await self.cache_manager.set(session_cache_key, current_routing.__dict__, ttl=1800)  # 30 min TTL
        
        return current_routing
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            "categories": self.categories,
            "category_embeddings_loaded": len(self.category_embeddings),
            "cache_available": self.cache_manager is not None,
            "openai_available": self.openai_client is not None,
            "claude_available": self.claude_client is not None
        }
