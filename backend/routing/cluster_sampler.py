"""
Cluster Sampler for intelligent document sampling and routing
"""

import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ClusterSample:
    """Sample from a cluster"""
    category: str
    documents: List[Dict[str, Any]]
    sample_size: int
    diversity_score: float

class ClusterSampler:
    """Intelligent cluster sampling for query routing"""
    
    def __init__(self):
        self.categories = ["legal", "technical", "financial", "hr", "general"]
        self.sample_sizes = {
            "legal": 5,
            "technical": 5,
            "financial": 5,
            "hr": 5,
            "general": 3
        }
        self.diversity_weights = {
            "legal": 0.8,  # High diversity for legal (different types of documents)
            "technical": 0.9,  # Very high diversity for technical (different technologies)
            "financial": 0.7,  # Medium diversity for financial (similar structure)
            "hr": 0.6,  # Lower diversity for HR (similar policies)
            "general": 0.5  # Lowest diversity for general (mixed content)
        }
    
    def sample_from_category(self, category: str, documents: List[Dict[str, Any]], 
                           max_samples: Optional[int] = None) -> ClusterSample:
        """Sample documents from a category with diversity"""
        if not documents:
            return ClusterSample(
                category=category,
                documents=[],
                sample_size=0,
                diversity_score=0.0
            )
        
        # Determine sample size
        sample_size = max_samples or self.sample_sizes.get(category, 3)
        sample_size = min(sample_size, len(documents))
        
        if sample_size >= len(documents):
            # Return all documents if sample size is larger than available
            diversity_score = self._calculate_diversity_score(documents)
            return ClusterSample(
                category=category,
                documents=documents,
                sample_size=len(documents),
                diversity_score=diversity_score
            )
        
        # Sample with diversity
        sampled_documents = self._diverse_sample(documents, sample_size, category)
        diversity_score = self._calculate_diversity_score(sampled_documents)
        
        return ClusterSample(
            category=category,
            documents=sampled_documents,
            sample_size=len(sampled_documents),
            diversity_score=diversity_score
        )
    
    def _diverse_sample(self, documents: List[Dict[str, Any]], sample_size: int, 
                       category: str) -> List[Dict[str, Any]]:
        """Sample documents with diversity"""
        if len(documents) <= sample_size:
            return documents
        
        diversity_weight = self.diversity_weights.get(category, 0.5)
        
        # If diversity weight is low, use random sampling
        if diversity_weight < 0.3:
            return random.sample(documents, sample_size)
        
        # Use stratified sampling for higher diversity
        sampled = []
        remaining_docs = documents.copy()
        
        # First, sample based on document types/sources
        doc_types = self._group_by_type(remaining_docs)
        
        # Sample from each type proportionally
        for doc_type, type_docs in doc_types.items():
            if not remaining_docs:
                break
            
            # Calculate how many to sample from this type
            type_ratio = len(type_docs) / len(documents)
            type_sample_size = max(1, int(sample_size * type_ratio))
            
            # Sample from this type
            if len(type_docs) <= type_sample_size:
                sampled.extend(type_docs)
                remaining_docs = [d for d in remaining_docs if d not in type_docs]
            else:
                type_sample = random.sample(type_docs, type_sample_size)
                sampled.extend(type_sample)
                remaining_docs = [d for d in remaining_docs if d not in type_sample]
        
        # If we need more samples, fill from remaining
        while len(sampled) < sample_size and remaining_docs:
            sampled.append(remaining_docs.pop(0))
        
        # If we have too many, randomly remove some
        if len(sampled) > sample_size:
            sampled = random.sample(sampled, sample_size)
        
        return sampled
    
    def _group_by_type(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group documents by type/source"""
        groups = {}
        
        for doc in documents:
            # Try to determine document type from metadata
            doc_type = "unknown"
            
            if "filename" in doc.get("metadata", {}):
                filename = doc["metadata"]["filename"].lower()
                if any(ext in filename for ext in [".pdf", ".doc", ".docx"]):
                    doc_type = "document"
                elif any(ext in filename for ext in [".txt", ".md"]):
                    doc_type = "text"
                elif any(ext in filename for ext in [".json", ".xml", ".yaml"]):
                    doc_type = "structured"
                else:
                    doc_type = "other"
            
            # Group by content length for diversity
            content_length = len(doc.get("content", ""))
            if content_length < 500:
                doc_type += "_short"
            elif content_length > 2000:
                doc_type += "_long"
            else:
                doc_type += "_medium"
            
            if doc_type not in groups:
                groups[doc_type] = []
            groups[doc_type].append(doc)
        
        return groups
    
    def _calculate_diversity_score(self, documents: List[Dict[str, Any]]) -> float:
        """Calculate diversity score for a set of documents"""
        if len(documents) <= 1:
            return 0.0
        
        # Calculate diversity based on:
        # 1. Document types
        # 2. Content length variation
        # 3. Source variation
        
        # Document types diversity
        doc_types = set()
        content_lengths = []
        sources = set()
        
        for doc in documents:
            # Document type
            if "filename" in doc.get("metadata", {}):
                filename = doc["metadata"]["filename"].lower()
                if ".pdf" in filename:
                    doc_types.add("pdf")
                elif ".txt" in filename:
                    doc_types.add("txt")
                elif ".md" in filename:
                    doc_types.add("md")
                else:
                    doc_types.add("other")
            
            # Content length
            content_lengths.append(len(doc.get("content", "")))
            
            # Source (filename without extension)
            if "filename" in doc.get("metadata", {}):
                source = doc["metadata"]["filename"].split(".")[0]
                sources.add(source)
        
        # Calculate diversity metrics
        type_diversity = len(doc_types) / 4.0  # Normalize to 0-1
        length_diversity = np.std(content_lengths) / (np.mean(content_lengths) + 1) if content_lengths else 0
        source_diversity = len(sources) / len(documents) if documents else 0
        
        # Weighted average
        diversity_score = (type_diversity * 0.4 + length_diversity * 0.3 + source_diversity * 0.3)
        
        return min(1.0, diversity_score)
    
    def sample_for_routing(self, category_documents: Dict[str, List[Dict[str, Any]]], 
                          max_total_samples: int = 20) -> Dict[str, ClusterSample]:
        """Sample documents from all categories for routing"""
        samples = {}
        total_docs = sum(len(docs) for docs in category_documents.values())
        
        if total_docs == 0:
            return samples
        
        # Calculate proportional sample sizes
        for category, documents in category_documents.items():
            if not documents:
                continue
            
            # Calculate sample size based on category importance and available documents
            category_ratio = len(documents) / total_docs
            base_sample_size = int(max_total_samples * category_ratio)
            
            # Adjust based on category priority
            category_weights = {
                "legal": 1.2,
                "technical": 1.1,
                "financial": 1.0,
                "hr": 0.9,
                "general": 0.8
            }
            
            weight = category_weights.get(category, 1.0)
            sample_size = max(1, int(base_sample_size * weight))
            
            # Sample from this category
            sample = self.sample_from_category(category, documents, sample_size)
            samples[category] = sample
        
        return samples
    
    def get_sampling_stats(self) -> Dict[str, Any]:
        """Get sampling statistics"""
        return {
            "categories": self.categories,
            "sample_sizes": self.sample_sizes,
            "diversity_weights": self.diversity_weights
        }
