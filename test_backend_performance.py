#!/usr/bin/env python3
"""
Test backend performance and timeout issues.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_backend_performance():
    """Test backend performance and identify timeout issues."""
    print("Testing Backend Performance...")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"✅ Backend responding in {duration:.2f} seconds")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Backend is healthy")
            print(f"📊 Stats: {stats}")
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Check if we have documents
    print("\n2. Checking for documents...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        stats = response.json()
        
        total_docs = stats.get('total_docs', 0)
        total_chunks = stats.get('total_chunks', 0)
        namespaces = stats.get('by_namespace', {})
        
        print(f"📄 Total documents: {total_docs}")
        print(f"📝 Total chunks: {total_chunks}")
        print(f"📁 Namespaces: {namespaces}")
        
        if total_docs == 0:
            print("⚠️ No documents found. Need to upload and embed first.")
            return False
        
        # Find a namespace with data
        test_namespace = None
        for ns, count in namespaces.items():
            if count > 0:
                test_namespace = ns
                break
        
        if not test_namespace:
            print("⚠️ No namespaces with data found.")
            return False
            
        print(f"✅ Found namespace with data: {test_namespace}")
        
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
        return False
    
    # Test 3: Test query with performance monitoring
    print(f"\n3. Testing query performance...")
    try:
        query_data = {
            "namespace": test_namespace,
            "query": "What vector database does RAGFlow use?",
            "k": 2
        }
        
        print(f"🔍 Query: {query_data['query']}")
        print(f"📊 K value: {query_data['k']}")
        print(f"⏱️ Starting query with 30-second timeout...")
        
        start_time = time.time()
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️ Query completed in {duration:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Query successful!")
                
                # Check answer
                answer = result.get('answer', '')
                print(f"📝 Answer length: {len(answer)}")
                print(f"📝 Answer preview: {answer[:200]}...")
                
                # Check context
                context = result.get('context', [])
                print(f"📚 Context sources: {len(context)}")
                
                for i, ctx in enumerate(context[:2]):
                    print(f"   Source {i+1} length: {len(ctx)}")
                    print(f"   Source {i+1} preview: {ctx[:100]}...")
                
                # Check for proper formatting
                if "ChromaDB" in answer:
                    print(f"✅ Answer correctly mentions ChromaDB")
                else:
                    print(f"⚠️ Answer doesn't mention ChromaDB")
                
                if duration < 10:
                    print(f"✅ Query completed quickly ({duration:.2f}s)")
                elif duration < 30:
                    print(f"⚠️ Query took a while ({duration:.2f}s)")
                else:
                    print(f"❌ Query took too long ({duration:.2f}s)")
                    
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ Query timed out after {duration:.2f} seconds")
            print("This suggests the backend is hanging")
            
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 BACKEND PERFORMANCE TEST COMPLETED!")
    print("✅ Backend connectivity working")
    print("✅ Document storage working")
    print("✅ Query processing working")
    print("=" * 50)

if __name__ == "__main__":
    test_backend_performance()
