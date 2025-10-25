#!/usr/bin/env python3
"""
Test script for RAGFlow backend functionality.
Run this after starting the server with: uvicorn app:app --reload --port 8000
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_upload_and_embed():
    """Test file upload and embedding with deduplication."""
    print("=== Testing Upload and Embed ===")
    
    # Create test files
    with open("test_a.txt", "w") as f:
        f.write("RAGFlow plugs docs into a vector DB and answers questions with sources.")
    
    with open("test_b.txt", "w") as f:
        f.write("RAGFlow uses Gemini embeddings and Claude for generation.")
    
    # Upload files
    print("Uploading files...")
    with open("test_a.txt", "rb") as f:
        resp_a = requests.post(f"{BASE_URL}/upload", files={"file": f})
    print(f"Upload A: {resp_a.json()}")
    
    with open("test_b.txt", "rb") as f:
        resp_b = requests.post(f"{BASE_URL}/upload", files={"file": f})
    print(f"Upload B: {resp_b.json()}")
    
    # Embed first file
    print("\nEmbedding first file...")
    embed_data = {
        "path": resp_a.json()["path"],
        "namespace": "demo"
    }
    resp_embed1 = requests.post(f"{BASE_URL}/embed", json=embed_data)
    result1 = resp_embed1.json()
    print(f"Embed 1: {result1}")
    
    # Embed second file
    print("\nEmbedding second file...")
    embed_data = {
        "path": resp_b.json()["path"],
        "namespace": "demo"
    }
    resp_embed2 = requests.post(f"{BASE_URL}/embed", json=embed_data)
    result2 = resp_embed2.json()
    print(f"Embed 2: {result2}")
    
    # Re-embed first file (should show deduplication)
    print("\nRe-embedding first file (dedup test)...")
    resp_embed3 = requests.post(f"{BASE_URL}/embed", json=embed_data)
    result3 = resp_embed3.json()
    print(f"Re-embed: {result3}")
    
    # Check if deduplication worked
    assert result3["chunks_added"] == 0, "Should have 0 chunks added on re-embed"
    assert result3["chunks_deduped"] > 0, "Should have deduplicated chunks"
    print("✅ Deduplication test passed!")
    
    return resp_a.json()["path"], resp_b.json()["path"]

def test_query():
    """Test querying with and without MMR reranking."""
    print("\n=== Testing Query ===")
    
    # Query without reranking
    print("Querying without reranking...")
    query_data = {
        "namespace": "demo",
        "query": "What does RAGFlow do?",
        "k": 4
    }
    resp_query1 = requests.post(f"{BASE_URL}/query", json=query_data)
    result1 = resp_query1.json()
    print(f"Query (no rerank): {result1}")
    
    # Query with MMR reranking
    print("\nQuerying with MMR reranking...")
    query_data["rerank"] = "mmr"
    resp_query2 = requests.post(f"{BASE_URL}/query", json=query_data)
    result2 = resp_query2.json()
    print(f"Query (MMR): {result2}")
    
    # Check results
    assert result1["rerank"] == "none", "Should have rerank=none"
    assert result2["rerank"] == "mmr", "Should have rerank=mmr"
    assert len(result1["context"]) > 0, "Should have context"
    assert len(result2["context"]) > 0, "Should have context"
    print("✅ Query test passed!")

def test_stats():
    """Test statistics endpoint."""
    print("\n=== Testing Stats ===")
    
    resp = requests.get(f"{BASE_URL}/stats")
    stats = resp.json()
    print(f"Stats: {stats}")
    
    # Check stats structure
    assert "total_vectors" in stats, "Should have total_vectors"
    assert "avg_chunk_length_chars" in stats, "Should have avg_chunk_length_chars"
    assert "by_namespace" in stats, "Should have by_namespace"
    assert "demo" in stats["by_namespace"], "Should have demo namespace"
    assert stats["total_vectors"] > 0, "Should have vectors"
    print("✅ Stats test passed!")

def test_cache():
    """Test embedding cache."""
    print("\n=== Testing Cache ===")
    
    cache_file = "./storage/cache/embeddings.jsonl"
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            lines = f.readlines()
        print(f"Cache file has {len(lines)} entries")
        print("✅ Cache file exists!")
    else:
        print("❌ Cache file not found")

def cleanup():
    """Clean up test files."""
    print("\n=== Cleanup ===")
    for file in ["test_a.txt", "test_b.txt"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")

def main():
    """Run all tests."""
    print("RAGFlow Backend Test Suite")
    print("=" * 40)
    
    try:
        # Test server is running
        resp = requests.get(f"{BASE_URL}/stats")
        if resp.status_code != 200:
            print("❌ Server not running. Start with: uvicorn app:app --reload --port 8000")
            return
        
        print("✅ Server is running")
        
        # Run tests
        test_upload_and_embed()
        test_query()
        test_stats()
        test_cache()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup()

if __name__ == "__main__":
    main()
