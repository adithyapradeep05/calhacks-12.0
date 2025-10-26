#!/usr/bin/env python3
"""
Check backend status and configuration.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def check_backend_status():
    """Check backend status and configuration."""
    print("Checking Backend Status...")
    print("=" * 40)
    
    try:
        # Check stats endpoint
        print("1. Checking stats endpoint...")
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats endpoint working")
            print(f"   Total docs: {stats.get('total_docs', 0)}")
            print(f"   Namespaces: {stats.get('by_namespace', {})}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
            
        # Check if we have documents
        print("\n2. Checking for documents...")
        if stats.get('total_docs', 0) > 0:
            print("✅ Documents found")
        else:
            print("❌ No documents found - need to upload and embed first")
            
        # Test a simple query
        print("\n3. Testing simple query...")
        query_data = {
            "namespace": "demo",
            "query": "test",
            "k": 1
        }
        
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            print(f"✅ Query endpoint working")
            print(f"   Response: {answer[:100]}...")
            
            # Check what type of response we got
            if "Based on the documents, here's what I can tell you:" in answer:
                print("⚠️ Hitting fallback response - Claude may have issues")
            elif "I'm not able to process your question properly" in answer:
                print("❌ Claude client not available")
            elif "I couldn't find any relevant information" in answer:
                print("❌ No context available")
            else:
                print("✅ Got proper Claude response")
        else:
            print(f"❌ Query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_backend_status()
