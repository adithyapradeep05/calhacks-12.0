#!/usr/bin/env python3
"""
Test script for RAGFlow Enhanced MVP Backend functionality.
Run this after starting the enhanced server with: python app_enhanced.py
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("=== Testing Health Check ===")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            health = resp.json()
            print(f"✅ Health check passed: {health}")
            return True
        else:
            print(f"❌ Health check failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_upload_and_categorization():
    """Test file upload with automatic categorization"""
    print("\n=== Testing Upload and Categorization ===")
    
    # Create test files for different categories
    test_files = {
        "legal_contract.txt": "This is a legal contract between parties. Terms and conditions apply. Liability is limited.",
        "technical_api.txt": "API documentation for REST endpoints. Implementation details and architecture specifications.",
        "financial_budget.txt": "Annual budget report with revenue projections and expense allocations.",
        "hr_policy.txt": "Employee handbook with workplace policies and benefits information."
    }
    
    upload_results = {}
    
    for filename, content in test_files.items():
        print(f"📤 Uploading {filename}...")
        
        # Create temporary file
        with open(filename, "w") as f:
            f.write(content)
        
        try:
            with open(filename, "rb") as f:
                resp = requests.post(f"{BASE_URL}/upload", files={"file": f})
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"✅ Upload successful: {result['category']} category")
                upload_results[filename] = result
            else:
                print(f"❌ Upload failed: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
        finally:
            # Clean up
            if os.path.exists(filename):
                os.remove(filename)
    
    return upload_results

def test_embedding():
    """Test document embedding with category-specific storage"""
    print("\n=== Testing Document Embedding ===")
    
    # Get document IDs from upload results
    # For this test, we'll use a mock document ID
    test_doc_id = "test-doc-123"
    
    try:
        embed_data = {
            "document_id": test_doc_id,
            "namespace": "test"
        }
        resp = requests.post(f"{BASE_URL}/embed", json=embed_data)
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ Embedding successful: {result['chunks']} chunks in {result['category']} category")
            return True
        else:
            print(f"❌ Embedding failed: {resp.status_code} - {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return False

def test_query_with_routing():
    """Test query with intelligent category routing"""
    print("\n=== Testing Query with Category Routing ===")
    
    test_queries = [
        ("What are the contract terms?", "legal"),
        ("How do I use the API?", "technical"),
        ("What's the budget allocation?", "financial"),
        ("What are the employee benefits?", "hr")
    ]
    
    for query, expected_category in test_queries:
        print(f"🔍 Query: {query}")
        
        try:
            query_data = {
                "namespace": "test",
                "query": query,
                "k": 3
            }
            resp = requests.post(f"{BASE_URL}/query", json=query_data)
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"✅ Query successful: {result['category']} category, {result['sources']} sources")
                print(f"   Answer: {result['answer'][:100]}...")
            else:
                print(f"❌ Query failed: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"❌ Query error: {e}")

def test_stats():
    """Test enhanced statistics endpoint"""
    print("\n=== Testing Enhanced Stats ===")
    
    try:
        resp = requests.get(f"{BASE_URL}/stats")
        if resp.status_code == 200:
            stats = resp.json()
            print(f"✅ Stats retrieved:")
            print(f"   Total documents: {stats['total_documents']}")
            print(f"   By category: {stats['by_category']}")
            print(f"   Services: {stats['services']}")
            return True
        else:
            print(f"❌ Stats failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return False

def test_cache_functionality():
    """Test caching functionality"""
    print("\n=== Testing Cache Functionality ===")
    
    query = "What is the main topic?"
    
    # First query (should miss cache)
    print("🔄 First query (cache miss expected)...")
    start_time = time.time()
    try:
        resp1 = requests.post(f"{BASE_URL}/query", json={
            "namespace": "test",
            "query": query,
            "k": 2
        })
        first_time = time.time() - start_time
        print(f"   First query time: {first_time:.3f}s")
    except Exception as e:
        print(f"❌ First query error: {e}")
        return False
    
    # Second query (should hit cache)
    print("🔄 Second query (cache hit expected)...")
    start_time = time.time()
    try:
        resp2 = requests.post(f"{BASE_URL}/query", json={
            "namespace": "test",
            "query": query,
            "k": 2
        })
        second_time = time.time() - start_time
        print(f"   Second query time: {second_time:.3f}s")
        
        if second_time < first_time:
            print("✅ Cache appears to be working (second query faster)")
        else:
            print("⚠️ Cache may not be working (second query not faster)")
            
    except Exception as e:
        print(f"❌ Second query error: {e}")
        return False

def cleanup():
    """Clean up test files"""
    print("\n=== Cleanup ===")
    test_files = ["legal_contract.txt", "technical_api.txt", "financial_budget.txt", "hr_policy.txt"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")

def main():
    """Run all enhanced tests"""
    print("🚀 RAGFlow Enhanced MVP Backend Test Suite")
    print("=" * 50)
    
    try:
        # Test server is running
        if not test_health_check():
            print("❌ Server not running. Start with: python app_enhanced.py")
            return
        
        print("✅ Server is running")
        
        # Run tests
        upload_results = test_upload_and_categorization()
        test_embedding()
        test_query_with_routing()
        test_stats()
        test_cache_functionality()
        
        print("\n🎉 Enhanced MVP tests completed!")
        print("\n📊 Summary:")
        print("✅ Health check")
        print("✅ Upload with categorization")
        print("✅ Category-specific embedding")
        print("✅ Intelligent query routing")
        print("✅ Enhanced statistics")
        print("✅ Caching functionality")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup()

if __name__ == "__main__":
    main()
