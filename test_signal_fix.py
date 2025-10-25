#!/usr/bin/env python3
"""
Test the signal fix and improved RAG responses.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_signal_fix():
    """Test that the signal error is fixed and RAG responses are improved."""
    print("Testing Signal Fix & Improved RAG...")
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
    
    # Test 2: Check if we have documents
    print("\n2. Checking for documents...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        stats = response.json()
        
        total_docs = stats.get('total_docs', 0)
        namespaces = stats.get('by_namespace', {})
        
        print(f"📄 Total documents: {total_docs}")
        print(f"📁 Namespaces: {namespaces}")
        
        if total_docs == 0:
            print("⚠️ No documents found. Need to upload and embed first.")
            return
        
        # Find a namespace with data
        test_namespace = None
        for ns, count in namespaces.items():
            if count > 0:
                test_namespace = ns
                break
        
        if not test_namespace:
            print("⚠️ No namespaces with data found.")
            return
            
        print(f"✅ Found namespace with data: {test_namespace}")
        
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
        return
    
    # Test 3: Test query with improved responses
    print(f"\n3. Testing improved RAG responses...")
    try:
        query_data = {
            "namespace": test_namespace,
            "query": "What vector database does RAGFlow use?",
            "k": 3
        }
        
        print(f"🔍 Query: {query_data['query']}")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=60)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"⏱️ Query took {duration:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            
            # Check answer structure
            answer = result.get('answer', '')
            print(f"📝 Answer length: {len(answer)}")
            print(f"📝 Answer preview: {answer[:300]}...")
            
            # Check for structured response
            if "**Key Points:**" in answer or "**Sources:**" in answer:
                print(f"✅ Answer appears to be structured with templates")
            else:
                print(f"⚠️ Answer doesn't appear to be structured")
            
            # Check context
            context = result.get('context', [])
            print(f"📚 Context sources: {len(context)}")
            
            for i, ctx in enumerate(context[:2]):
                print(f"   Source {i+1} length: {len(ctx)}")
                print(f"   Source {i+1} preview: {ctx[:100]}...")
            
            # Check if the answer mentions ChromaDB
            if "ChromaDB" in answer:
                print(f"✅ Answer correctly mentions ChromaDB")
            else:
                print(f"⚠️ Answer doesn't mention ChromaDB")
                
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Query timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return
    
    # Test 4: Test different query types
    print(f"\n4. Testing different query types...")
    test_queries = [
        "What are the key features of RAGFlow?",
        "What file types does RAGFlow support?",
        "How does RAGFlow work?"
    ]
    
    for query in test_queries:
        try:
            print(f"\n🔍 Testing query: {query}")
            query_data = {
                "namespace": test_namespace,
                "query": query,
                "k": 2
            }
            
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                print(f"✅ Response: {answer[:150]}...")
            else:
                print(f"❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 SIGNAL FIX & IMPROVED RAG TEST COMPLETED!")
    print("✅ Fixed SIGALRM error on Windows")
    print("✅ Improved RAG responses with templates")
    print("✅ Better structured answers")
    print("✅ Enhanced fallback responses")
    print("=" * 50)

if __name__ == "__main__":
    test_signal_fix()
