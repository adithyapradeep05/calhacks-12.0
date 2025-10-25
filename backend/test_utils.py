#!/usr/bin/env python3
"""
Unit tests for RAGFlow utility functions.
"""

import unittest
import hashlib
import math

def normalize_text(s: str) -> str:
    """Normalize text by lowercasing and squeezing whitespace."""
    import re
    return re.sub(r'\s+', ' ', s.lower().strip())

def md5_hash(s: str) -> str:
    """Compute MD5 hash of a string."""
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def truncate_chunk(chunk: str, max_length: int = 6000) -> str:
    """Truncate chunk to max_length characters."""
    return chunk[:max_length]

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)

def l2_norm(vector):
    """Compute L2 norm of a vector."""
    return math.sqrt(sum(x * x for x in vector))

def mmr_rerank(query_vector, candidate_vectors, top_k, lambda_param=0.5):
    """MMR reranking algorithm."""
    if not candidate_vectors:
        return []
    
    n = len(candidate_vectors)
    if n <= top_k:
        return list(range(n))
    
    # Initialize with most relevant document
    similarities = [cosine_similarity(query_vector, vec) for vec in candidate_vectors]
    selected = [similarities.index(max(similarities))]
    remaining = set(range(n)) - set(selected)
    
    # Iteratively select documents that maximize MMR score
    while len(selected) < top_k and remaining:
        best_score = -float('inf')
        best_idx = None
        
        for idx in remaining:
            # Relevance to query
            relevance = similarities[idx]
            
            # Maximum similarity to already selected documents
            max_sim = 0
            for sel_idx in selected:
                sim = cosine_similarity(candidate_vectors[idx], candidate_vectors[sel_idx])
                max_sim = max(max_sim, sim)
            
            # MMR score
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx
        
        if best_idx is not None:
            selected.append(best_idx)
            remaining.remove(best_idx)
        else:
            break
    
    return selected

class TestUtils(unittest.TestCase):
    
    def test_normalize_text(self):
        """Test text normalization."""
        self.assertEqual(normalize_text("  Hello   World  "), "hello world")
        self.assertEqual(normalize_text("UPPERCASE"), "uppercase")
        self.assertEqual(normalize_text("Multiple    Spaces"), "multiple spaces")
        self.assertEqual(normalize_text(""), "")
    
    def test_md5_hash(self):
        """Test MD5 hashing."""
        # Test deterministic hashing
        hash1 = md5_hash("test")
        hash2 = md5_hash("test")
        self.assertEqual(hash1, hash2)
        
        # Test different inputs produce different hashes
        hash3 = md5_hash("different")
        self.assertNotEqual(hash1, hash3)
        
        # Test empty string
        hash_empty = md5_hash("")
        self.assertEqual(len(hash_empty), 32)  # MD5 produces 32-char hex
    
    def test_truncate_chunk(self):
        """Test chunk truncation."""
        # Test normal truncation
        text = "a" * 100
        truncated = truncate_chunk(text, 50)
        self.assertEqual(len(truncated), 50)
        self.assertEqual(truncated, "a" * 50)
        
        # Test no truncation needed
        text = "short"
        truncated = truncate_chunk(text, 100)
        self.assertEqual(truncated, "short")
        
        # Test empty string
        truncated = truncate_chunk("", 100)
        self.assertEqual(truncated, "")
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        # Test identical vectors
        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        sim = cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(sim, 1.0, places=5)
        
        # Test orthogonal vectors
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        sim = cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(sim, 0.0, places=5)
        
        # Test opposite vectors
        vec1 = [1, 0, 0]
        vec2 = [-1, 0, 0]
        sim = cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(sim, -1.0, places=5)
        
        # Test zero vectors
        vec1 = [0, 0, 0]
        vec2 = [1, 1, 1]
        sim = cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(sim, 0.0, places=5)
    
    def test_l2_norm(self):
        """Test L2 norm calculation."""
        # Test unit vector
        vec = [1, 0, 0]
        norm = l2_norm(vec)
        self.assertAlmostEqual(norm, 1.0, places=5)
        
        # Test zero vector
        vec = [0, 0, 0]
        norm = l2_norm(vec)
        self.assertAlmostEqual(norm, 0.0, places=5)
        
        # Test 3D vector
        vec = [3, 4, 0]
        norm = l2_norm(vec)
        self.assertAlmostEqual(norm, 5.0, places=5)
    
    def test_mmr_rerank(self):
        """Test MMR reranking algorithm."""
        # Test with identical vectors (should return first k)
        query = [1, 0, 0]
        candidates = [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
        result = mmr_rerank(query, candidates, 2)
        self.assertEqual(len(result), 2)
        self.assertIn(0, result)
        
        # Test with diverse vectors
        query = [1, 0, 0]
        candidates = [
            [1, 0, 0],  # Most relevant
            [0, 1, 0],  # Different direction
            [0, 0, 1],  # Different direction
            [0.9, 0.1, 0]  # Similar to first
        ]
        result = mmr_rerank(query, candidates, 3)
        self.assertEqual(len(result), 3)
        self.assertIn(0, result)  # Most relevant should be included
        
        # Test empty candidates
        result = mmr_rerank(query, [], 2)
        self.assertEqual(result, [])
        
        # Test k larger than candidates
        result = mmr_rerank(query, candidates, 10)
        self.assertEqual(len(result), len(candidates))

if __name__ == "__main__":
    unittest.main()
