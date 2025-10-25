#!/usr/bin/env python3
"""
Debug the query issue - test if the backend is working properly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_query_debug():
    """Debug the query issue step by step."""
    print("Debugging Query Issue...")
    print("=" * 40)
    
    # Test 1: Check if backend is running
    print("\n1. Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running")
            stats = response.json()
            print(f"Stats: {stats}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test 2: Check if we have any documents
    print("\n2. Checking for existing documents...")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"Total documents: {stats.get('total_docs', 0)}")
            print(f"Total chunks: {stats.get('total_chunks', 0)}")
            print(f"Namespaces: {stats.get('by_namespace', {})}")
            
            if stats.get('total_docs', 0) == 0:
                print("⚠️ No documents found. Need to upload and embed first.")
                return
        else:
            print(f"❌ Stats check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
        return
    
    # Test 3: Test a simple query
    print("\n3. Testing simple query...")
    try:
        query_data = {
            "namespace": "demo",  # Try common namespace
            "query": "What is RAGFlow?",
            "k": 3
        }
        
        print(f"Sending query: {query_data}")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Query took {duration:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"Answer: {result.get('answer', 'No answer')[:200]}...")
            print(f"Context sources: {len(result.get('context', []))}")
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            return
    except requests.exceptions.Timeout:
        print("❌ Query timed out after 30 seconds")
        return
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return
    
    # Test 4: Test with different namespace
    print("\n4. Testing with different namespace...")
    try:
        # Try to find a namespace that exists
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            namespaces = stats.get('by_namespace', {})
            
            if namespaces:
                # Use the first available namespace
                test_namespace = list(namespaces.keys())[0]
                print(f"Testing with namespace: {test_namespace}")
                
                query_data = {
                    "namespace": test_namespace,
                    "query": "What vector database does this use?",
                    "k": 3
                }
                
                start_time = time.time()
                response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"Query took {duration:.2f} seconds")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Query successful!")
                    print(f"Answer: {result.get('answer', 'No answer')}")
                    print(f"Context sources: {len(result.get('context', []))}")
                else:
                    print(f"❌ Query failed: {response.status_code}")
                    print(f"Error: {response.text}")
            else:
                print("⚠️ No namespaces found. Need to upload and embed documents first.")
    except Exception as e:
        print(f"❌ Namespace test failed: {e}")
        return
    
    print("\n" + "=" * 40)
    print("Query debugging completed!")

if __name__ == "__main__":
    test_query_debug()
