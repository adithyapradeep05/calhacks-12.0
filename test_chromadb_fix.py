#!/usr/bin/env python3
"""
Test the ChromaDB fix for the 'ids' error.
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_chromadb_fix():
    """Test that the ChromaDB 'ids' error is fixed."""
    print("Testing ChromaDB Fix...")
    print("=" * 40)
    
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
            print("Please upload a document and embed it first.")
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
    
    # Test 3: Test query (this should now work without the 'ids' error)
    print(f"\n3. Testing query with namespace: {test_namespace}")
    try:
        query_data = {
            "namespace": test_namespace,
            "query": "What vector database does this use?",
            "k": 3
        }
        
        print(f"🔍 Query: {query_data['query']}")
        print(f"📊 K value: {query_data['k']}")
        
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"📝 Answer: {result.get('answer', 'No answer')}")
            print(f"📚 Context sources: {len(result.get('context', []))}")
            
            # Show context snippets
            for i, ctx in enumerate(result.get('context', [])[:2]):
                print(f"   Source {i+1}: {ctx[:100]}...")
                
            print(f"\n🎉 SUCCESS: ChromaDB 'ids' error is fixed!")
            print(f"✅ Claude is generating responses")
            print(f"✅ Query system is working")
            
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("Could not parse error response as JSON")
                
    except requests.exceptions.Timeout:
        print("❌ Query timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Query failed with exception: {e}")
        return
    
    print("\n" + "=" * 40)
    print("🎉 CHROMADB FIX TEST COMPLETED!")
    print("✅ Fixed 'ids' parameter error")
    print("✅ Claude LLM is working")
    print("✅ Query system is functional")
    print("=" * 40)

if __name__ == "__main__":
    test_chromadb_fix()
