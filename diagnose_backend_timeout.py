#!/usr/bin/env python3
"""
Diagnose backend timeout issues.
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def diagnose_backend_timeout():
    """Diagnose why the backend is timing out."""
    print("Diagnosing Backend Timeout Issues...")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"✅ Backend responding in {duration:.2f} seconds")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"Stats: {stats}")
        else:
            print(f"❌ Backend returned {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure the backend is running with: cd backend && python run.py")
        return
    
    # Test 2: Check environment variables
    print("\n2. Checking environment variables...")
    try:
        # Check if .env file exists
        env_file = "backend/.env"
        if os.path.exists(env_file):
            print(f"✅ .env file exists: {env_file}")
            with open(env_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        key = line.split('=')[0]
                        if 'API_KEY' in key:
                            print(f"   {key}: {'Set' if 'your_' not in line else 'Not set'}")
        else:
            print(f"❌ .env file not found: {env_file}")
            print("Create backend/.env with your API keys")
    except Exception as e:
        print(f"❌ Error checking environment: {e}")
    
    # Test 3: Test simple query with timing
    print("\n3. Testing simple query with detailed timing...")
    try:
        # First check if we have documents
        response = requests.get(f"{BASE_URL}/stats")
        stats = response.json()
        
        total_docs = stats.get('total_docs', 0)
        namespaces = stats.get('by_namespace', {})
        
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
        
        # Test query with detailed timing
        query_data = {
            "namespace": test_namespace,
            "query": "What is this document about?",
            "k": 2
        }
        
        print(f"🔍 Testing query: {query_data['query']}")
        print(f"📊 K value: {query_data['k']}")
        print(f"⏱️ Starting query with 60-second timeout...")
        
        start_time = time.time()
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=60)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️ Query completed in {duration:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Query successful!")
                print(f"📝 Answer length: {len(result.get('answer', ''))}")
                print(f"📚 Context sources: {len(result.get('context', []))}")
                print(f"📝 Answer preview: {result.get('answer', '')[:100]}...")
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ Query timed out after {duration:.2f} seconds")
            print("This suggests the backend is hanging or very slow")
            
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return
    
    # Test 4: Check backend logs
    print("\n4. Backend diagnostic recommendations...")
    print("Check your backend terminal for:")
    print("- API key errors")
    print("- ChromaDB connection issues")
    print("- Claude API errors")
    print("- OpenAI API errors")
    print("- Memory issues")
    print("- Network connectivity")
    
    print("\nCommon causes of timeouts:")
    print("- Missing or invalid API keys")
    print("- ChromaDB database corruption")
    print("- Network connectivity issues")
    print("- API rate limits")
    print("- Backend process hanging")
    
    print("\n" + "=" * 50)
    print("Backend timeout diagnosis complete!")
    print("Check the recommendations above and your backend logs.")

if __name__ == "__main__":
    diagnose_backend_timeout()
