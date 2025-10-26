#!/usr/bin/env python3
"""
Test a simple query to see what's happening.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_simple_query():
    """Test a simple query."""
    print("Testing Simple Query...")
    print("=" * 30)
    
    query_data = {
        "namespace": "test",
        "query": "What is the technical architecture?",
        "k": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            context = result.get('context', [])
            
            print(f"Answer: {answer}")
            print(f"Context items: {len(context)}")
            
            # Check if it's the new format
            if "**Answer:**" in answer:
                print("SUCCESS: Using new RAGFlow format")
            else:
                print("WARNING: Not using new format")
                
        else:
            print(f"FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_simple_query()