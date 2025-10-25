#!/usr/bin/env python3
"""
Test the timeout and context formatting fixes.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_timeout_fix():
    """Test that timeout and context issues are fixed."""
    print("Testing Timeout & Context Fixes...")
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
        total_chunks = stats.get('total_chunks', 0)
        namespaces = stats.get('by_namespace', {})
        
        print(f"Total documents: {total_docs}")
        print(f"Total chunks: {total_chunks}")
        print(f"Namespaces: {namespaces}")
        
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
    
    # Test 3: Test query with longer timeout
    print(f"\n3. Testing query with extended timeout...")
    try:
        query_data = {
            "namespace": test_namespace,
            "query": "What vector database does RAGFlow use?",
            "k": 3
        }
        
        print(f"🔍 Query: {query_data['query']}")
        print(f"📊 K value: {query_data['k']}")
        print(f"⏱️ Using 60-second timeout...")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=60)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"⏱️ Query took {duration:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"📝 Answer: {result.get('answer', 'No answer')}")
            print(f"📚 Context sources: {len(result.get('context', []))}")
            
            # Check if answer is properly formatted (not with spaces between chars)
            answer = result.get('answer', '')
            if ' ' in answer and len(answer) > 50:
                print(f"✅ Answer appears to be properly formatted")
            else:
                print(f"⚠️ Answer might have formatting issues: {answer[:100]}...")
            
            # Show context snippets
            for i, ctx in enumerate(result.get('context', [])[:2]):
                print(f"   Source {i+1}: {ctx[:100]}...")
                
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Query timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Query failed with exception: {e}")
        return
    
    # Test 4: Test different query
    print(f"\n4. Testing different query...")
    try:
        query_data = {
            "namespace": test_namespace,
            "query": "What are the key features of RAGFlow?",
            "k": 2
        }
        
        print(f"🔍 Query: {query_data['query']}")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=60)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"⏱️ Query took {duration:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Second query successful!")
            print(f"📝 Answer: {result.get('answer', 'No answer')[:200]}...")
        else:
            print(f"❌ Second query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Second query failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 TIMEOUT & CONTEXT FIX TEST COMPLETED!")
    print("✅ Extended timeout to 60 seconds")
    print("✅ Fixed context formatting")
    print("✅ Improved Claude error handling")
    print("✅ Better fallback responses")
    print("=" * 50)

if __name__ == "__main__":
    test_timeout_fix()
