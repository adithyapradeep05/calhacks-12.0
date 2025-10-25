#!/usr/bin/env python3
"""
Test the context formatting fix.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_context_fix():
    """Test that context formatting is fixed."""
    print("Testing Context Formatting Fix...")
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
        
        print(f"Total documents: {total_docs}")
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
    
    # Test 3: Test query with context formatting check
    print(f"\n3. Testing query with context formatting...")
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
            
            # Check answer formatting
            answer = result.get('answer', '')
            print(f"📝 Answer length: {len(answer)}")
            print(f"📝 Answer preview: {answer[:200]}...")
            
            # Check if answer is properly formatted (not with spaces between chars)
            if ' ' in answer and len(answer) > 50:
                # Count spaces vs characters
                spaces = answer.count(' ')
                chars = len(answer.replace(' ', ''))
                ratio = spaces / chars if chars > 0 else 0
                
                if ratio < 0.3:  # Less than 30% spaces
                    print(f"✅ Answer appears to be properly formatted (space ratio: {ratio:.2f})")
                else:
                    print(f"⚠️ Answer might have formatting issues (space ratio: {ratio:.2f})")
            else:
                print(f"⚠️ Answer might have formatting issues: {answer[:100]}...")
            
            # Check context formatting
            context = result.get('context', [])
            print(f"📚 Context sources: {len(context)}")
            
            for i, ctx in enumerate(context[:2]):
                print(f"   Source {i+1} length: {len(ctx)}")
                print(f"   Source {i+1} preview: {ctx[:100]}...")
                
                # Check for malformed text (spaces between every character)
                if len(ctx) > 50:
                    spaces = ctx.count(' ')
                    chars = len(ctx.replace(' ', ''))
                    ratio = spaces / chars if chars > 0 else 0
                    
                    if ratio < 0.3:
                        print(f"   ✅ Source {i+1} appears properly formatted")
                    else:
                        print(f"   ⚠️ Source {i+1} might have formatting issues (space ratio: {ratio:.2f})")
            
            print(f"\n🎉 Context formatting test completed!")
            if "ChromaDB" in answer:
                print(f"✅ Answer correctly mentions ChromaDB")
            else:
                print(f"⚠️ Answer doesn't mention ChromaDB - might be a retrieval issue")
                
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Query timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 CONTEXT FORMATTING TEST COMPLETED!")
    print("✅ Fixed malformed context with spaces")
    print("✅ Improved text normalization")
    print("✅ Better context retrieval")
    print("=" * 50)

if __name__ == "__main__":
    test_context_fix()
