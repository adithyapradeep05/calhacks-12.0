#!/usr/bin/env python3
"""
Simple diagnostic for 500 error.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def diagnose_500_simple():
    """Simple diagnostic for 500 error."""
    print("Diagnosing 500 Error...")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Backend is running")
            print(f"Stats: {stats}")
        else:
            print(f"❌ Backend returned {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        print("Make sure the backend is running with: cd backend && python run.py")
        return False
    except Exception as e:
        print(f"ERROR: Connection error: {e}")
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
            print("Please upload a document and embed it first.")
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
    
    # Test 3: Test simple query
    print(f"\n3. Testing simple query...")
    try:
        query_data = {
            "namespace": test_namespace,
            "query": "What is this document about?",
            "k": 2
        }
        
        print(f"🔍 Query: {query_data['query']}")
        print(f"📊 Namespace: {query_data['namespace']}")
        print(f"📊 K value: {query_data['k']}")
        
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"📝 Answer: {result.get('answer', 'No answer')[:200]}...")
            print(f"📚 Context: {len(result.get('context', []))} sources")
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
        print(f"❌ Query failed: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 DIAGNOSTIC COMPLETED!")
    print("Check the results above to identify the issue.")
    print("=" * 40)

if __name__ == "__main__":
    diagnose_500_simple()
