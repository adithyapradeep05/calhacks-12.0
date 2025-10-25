#!/usr/bin/env python3
"""
Simple test to check if backend is working.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test basic backend health."""
    print("Testing Backend Health...")
    print("=" * 30)
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"✅ Backend responding in {duration:.2f} seconds")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Backend is healthy")
            print(f"📊 Stats: {stats}")
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Backend not responding (timeout)")
        return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure the backend is running with: cd backend && python run.py")
        return False
    
    # Test 2: Check if we have documents
    print("\n2. Checking for documents...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        stats = response.json()
        
        total_docs = stats.get('total_docs', 0)
        total_chunks = stats.get('total_chunks', 0)
        
        print(f"📄 Total documents: {total_docs}")
        print(f"📝 Total chunks: {total_chunks}")
        
        if total_docs == 0:
            print("⚠️ No documents found. Need to upload and embed first.")
            print("Please upload a document and embed it first.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking documents: {e}")
        return False

if __name__ == "__main__":
    if test_backend_health():
        print("\n✅ Backend is healthy and ready!")
    else:
        print("\n❌ Backend has issues. Check the errors above.")
