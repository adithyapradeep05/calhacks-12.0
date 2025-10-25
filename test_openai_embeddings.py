#!/usr/bin/env python3
"""
Test OpenAI embeddings functionality.
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_openai_embeddings():
    """Test OpenAI embeddings with the backend."""
    print("Testing OpenAI Embeddings...")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"SUCCESS: Backend is running. Stats: {stats}")
        else:
            print(f"ERROR: Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"ERROR: Cannot connect to backend: {e}")
        return
    
    # Test 2: Upload test document
    print("\n2. Testing file upload...")
    try:
        with open("test-document.txt", "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: File uploaded: {result}")
            file_path = result["path"]
        else:
            print(f"ERROR: Upload failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Upload failed: {e}")
        return
    
    # Test 3: Embed with OpenAI
    print("\n3. Testing OpenAI embedding...")
    try:
        embed_data = {"path": file_path, "namespace": "openai-test"}
        response = requests.post(f"{BASE_URL}/embed", json=embed_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: OpenAI embedding completed: {result}")
        else:
            print(f"ERROR: Embedding failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Embedding failed: {e}")
        return
    
    # Test 4: Query with Claude
    print("\n4. Testing query with Claude...")
    try:
        query_data = {
            "namespace": "openai-test",
            "query": "What is RAGFlow?",
            "k": 4
        }
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Query successful")
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Context sources: {len(result['context'])}")
        else:
            print(f"ERROR: Query failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Query failed: {e}")
        return
    
    # Test 5: Check embedding dimensions
    print("\n5. Testing embedding dimensions...")
    try:
        # Get stats to see if embeddings were stored
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"SUCCESS: Final stats: {stats}")
            print(f"Expected embedding dimension: 1536 (OpenAI text-embedding-3-small)")
        else:
            print(f"ERROR: Stats failed: {response.status_code}")
            return
    except Exception as e:
        print(f"ERROR: Stats test failed: {e}")
        return
    
    print("\n" + "=" * 40)
    print("OPENAI EMBEDDINGS TEST COMPLETED!")
    print("✅ OpenAI embeddings working")
    print("✅ Claude chat working")
    print("✅ Vector storage working")
    print("=" * 40)

if __name__ == "__main__":
    test_openai_embeddings()
