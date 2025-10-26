#!/usr/bin/env python3
"""
Check what documents are stored in the namespace.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def check_documents():
    """Check what documents are stored."""
    print("Checking Stored Documents...")
    print("=" * 40)
    
    try:
        # Get stats to see what's stored
        print("1. Getting stats...")
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print("SUCCESS: Got stats")
            print(f"Total docs: {stats.get('total_docs', 0)}")
            print(f"Namespaces: {stats.get('by_namespace', {})}")
            
            # Check each namespace
            for namespace, count in stats.get('by_namespace', {}).items():
                print(f"\nNamespace '{namespace}': {count} documents")
                
                # Try to query each namespace to see what's there
                print(f"Testing query in namespace '{namespace}'...")
                query_data = {
                    "namespace": namespace,
                    "query": "What documents are available?",
                    "k": 5  # Get more results
                }
                
                response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', '')
                    context = result.get('context', [])
                    
                    print(f"  Query response: {answer[:100]}...")
                    print(f"  Context items: {len(context)}")
                    
                    # Show context previews
                    for i, ctx in enumerate(context[:3]):
                        print(f"  Context {i+1}: {ctx[:80]}...")
                else:
                    print(f"  Query failed: {response.status_code}")
        else:
            print(f"FAILED: Stats {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_documents()
