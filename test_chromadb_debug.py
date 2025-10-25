#!/usr/bin/env python3
"""
Debug ChromaDB storage and retrieval issues.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chromadb_debug():
    """Debug ChromaDB storage and retrieval."""
    print("Debugging ChromaDB Storage & Retrieval...")
    print("=" * 50)
    
    # Test 1: Check backend health
    print("\n1. Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Backend is running")
            print(f"Stats: {stats}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test 2: Upload a simple test document
    print("\n2. Uploading test document...")
    try:
        # Create a simple test document
        test_content = "RAGFlow is a document processing system. It uses ChromaDB as the vector database. The system supports PDF, TXT, and Markdown files."
        
        with open("debug-test.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        with open("debug-test.txt", "rb") as f:
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
    
    # Test 3: Embed the document
    print("\n3. Embedding document...")
    try:
        embed_data = {"path": file_path, "namespace": "debug-test"}
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
    
    # Test 4: Query the document
    print("\n4. Querying document...")
    try:
        query_data = {
            "namespace": "debug-test",
            "query": "What vector database does RAGFlow use?",
            "k": 2
        }
        
        print(f"🔍 Query: {query_data['query']}")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"⏱️ Query took {duration:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            
            # Check answer
            answer = result.get('answer', '')
            print(f"📝 Answer: {answer}")
            
            # Check context
            context = result.get('context', [])
            print(f"📚 Context sources: {len(context)}")
            
            for i, ctx in enumerate(context):
                print(f"   Source {i+1}: {ctx}")
                
            # Check if the answer mentions ChromaDB
            if "ChromaDB" in answer:
                print(f"✅ Answer correctly mentions ChromaDB")
            else:
                print(f"⚠️ Answer doesn't mention ChromaDB")
                print(f"   This suggests the context retrieval is not working properly")
                
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Query timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return
    
    # Test 5: Check stats after embedding
    print("\n5. Checking stats after embedding...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        stats = response.json()
        print(f"📊 Final stats: {stats}")
        
        # Check if our namespace is in the stats
        namespaces = stats.get('by_namespace', {})
        if 'debug-test' in namespaces:
            print(f"✅ Namespace 'debug-test' found in stats")
        else:
            print(f"⚠️ Namespace 'debug-test' not found in stats")
            
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 CHROMADB DEBUG TEST COMPLETED!")
    print("Check the backend logs for debug information about:")
    print("- Text extraction")
    print("- Chunking process")
    print("- ChromaDB storage")
    print("- ChromaDB retrieval")
    print("=" * 50)

if __name__ == "__main__":
    test_chromadb_debug()
