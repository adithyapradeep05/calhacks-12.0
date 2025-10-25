#!/usr/bin/env python3
"""
Debug the 500 error in the query endpoint.
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def debug_500_error():
    """Debug the 500 error step by step."""
    print("Debugging 500 Error...")
    print("=" * 40)
    
    # Test 1: Check backend health
    print("\n1. Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        print(f"Health check: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Backend is running")
            print(f"Stats: {stats}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            print(f"Response: {response.text}")
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
    
    # Test 3: Test simple query
    print(f"\n3. Testing query with namespace: {test_namespace}")
    try:
        query_data = {
            "namespace": test_namespace,
            "query": "What is this document about?",
            "k": 2
        }
        
        print(f"Query data: {query_data}")
        
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"Answer: {result.get('answer', 'No answer')}")
            print(f"Context: {len(result.get('context', []))} sources")
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
    
    # Test 4: Check backend logs
    print("\n4. Backend configuration check...")
    print("Check your backend terminal for error messages.")
    print("Common issues:")
    print("- Missing ANTHROPIC_API_KEY")
    print("- ChromaDB connection issues")
    print("- OpenAI API key problems")
    print("- Model configuration errors")
    
    print("\n" + "=" * 40)
    print("500 Error Debugging Complete!")
    print("Check the error details above and your backend logs.")

if __name__ == "__main__":
    debug_500_error()
