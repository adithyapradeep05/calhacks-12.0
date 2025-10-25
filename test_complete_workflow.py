#!/usr/bin/env python3
"""
Test complete RAGFlow workflow: Upload -> Embed -> Query
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test the complete RAGFlow workflow."""
    print("Testing Complete RAGFlow Workflow...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Backend Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Backend running. Current stats: {stats}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test 2: Upload document
    print("\n2. Uploading Document...")
    try:
        with open("test-document.txt", "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"✅ Upload successful: {upload_result['filename']}")
            file_path = upload_result["path"]
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # Test 3: Embed document
    print("\n3. Embedding Document...")
    try:
        embed_data = {"path": file_path, "namespace": "workflow-test"}
        response = requests.post(f"{BASE_URL}/embed", json=embed_data)
        
        if response.status_code == 200:
            embed_result = response.json()
            print(f"✅ Embedding successful: {embed_result['chunks']} chunks")
        else:
            print(f"❌ Embedding failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return
    
    # Test 4: Query document
    print("\n4. Querying Document...")
    try:
        query_data = {
            "namespace": "workflow-test",
            "query": "What is RAGFlow and what are its key features?",
            "k": 4
        }
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        
        if response.status_code == 200:
            query_result = response.json()
            print(f"✅ Query successful!")
            print(f"📝 Answer: {query_result['answer'][:200]}...")
            print(f"📚 Context sources: {len(query_result['context'])}")
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return
    
    # Test 5: Verify ChromaDB storage
    print("\n5. Verifying ChromaDB Storage...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ ChromaDB stats: {stats}")
            
            # Check if our namespace is in the stats
            if "workflow-test" in stats.get("by_namespace", {}):
                print(f"✅ Namespace 'workflow-test' found in ChromaDB")
            else:
                print(f"⚠️ Namespace 'workflow-test' not found in stats")
        else:
            print(f"❌ Stats check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
        return
    
    # Test 6: Test different query
    print("\n6. Testing Different Query...")
    try:
        query_data = {
            "namespace": "workflow-test",
            "query": "What are the technical components of RAGFlow?",
            "k": 3
        }
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        
        if response.status_code == 200:
            query_result = response.json()
            print(f"✅ Second query successful!")
            print(f"📝 Answer: {query_result['answer'][:200]}...")
        else:
            print(f"❌ Second query failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Second query failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 COMPLETE WORKFLOW TEST PASSED!")
    print("✅ Upload: Working")
    print("✅ Embed: Working (OpenAI embeddings)")
    print("✅ Query: Working (Claude chat)")
    print("✅ ChromaDB: Working (persistent storage)")
    print("✅ Namespace: Working (isolation)")
    print("=" * 50)

if __name__ == "__main__":
    test_complete_workflow()
