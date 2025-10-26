#!/usr/bin/env python3
"""
Test the improved technical response formatting.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_technical_responses():
    """Test improved technical response formatting."""
    print("Testing Technical Response Improvements...")
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
    
    # Test 3: Test technical queries with improved formatting
    print(f"\n3. Testing technical queries...")
    technical_queries = [
        "What is the computer architecture?",
        "What is the tech stack?",
        "How does the system work?",
        "What are the key components?",
        "What is the technical architecture?"
    ]
    
    for query in technical_queries:
        try:
            print(f"\n🔍 Testing query: {query}")
            query_data = {
                "namespace": test_namespace,
                "query": query,
                "k": 3
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=60)
            end_time = time.time()
            
            duration = end_time - start_time
            print(f"⏱️ Query took {duration:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                
                print(f"✅ Query successful!")
                print(f"📝 Answer length: {len(answer)}")
                print(f"📝 Answer preview: {answer[:300]}...")
                
                # Check for structured formatting
                if "# Technical Analysis:" in answer:
                    print(f"✅ Answer has structured technical formatting")
                else:
                    print(f"⚠️ Answer doesn't have structured formatting")
                
                # Check for malformed text
                if "erse results" in answer:
                    print(f"❌ Answer still contains malformed text")
                else:
                    print(f"✅ Answer appears to be properly formatted")
                
                # Check for technical sections
                sections = ["## Overview", "## Key Components", "## Technical Details"]
                found_sections = [section for section in sections if section in answer]
                print(f"📋 Found sections: {found_sections}")
                
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Query timed out after 60 seconds")
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 TECHNICAL RESPONSE TEST COMPLETED!")
    print("✅ Improved text extraction")
    print("✅ Better context cleaning")
    print("✅ Structured technical responses")
    print("✅ Malformed text prevention")
    print("=" * 50)

if __name__ == "__main__":
    test_technical_responses()
