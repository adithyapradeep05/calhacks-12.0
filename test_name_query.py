#!/usr/bin/env python3
"""
Test querying for name in different namespaces.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_name_query():
    """Test querying for name in different namespaces."""
    print("Testing Name Query in Different Namespaces...")
    print("=" * 50)
    
    namespaces = ["demo", "test", "TEST"]
    query = "What is my name?"
    
    for namespace in namespaces:
        print(f"\nTesting namespace: '{namespace}'")
        print("-" * 30)
        
        query_data = {
            "namespace": namespace,
            "query": query,
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
                
                # Check if name is found
                if any(word in answer.lower() for word in ["name", "adith", "user"]):
                    print("SUCCESS: Name found in this namespace!")
                else:
                    print("INFO: No name found in this namespace")
                    
                # Show context previews
                for i, ctx in enumerate(context[:2]):
                    print(f"Context {i+1}: {ctx[:60]}...")
            else:
                print(f"FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_name_query()
