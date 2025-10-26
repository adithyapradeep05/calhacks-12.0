#!/usr/bin/env python3
"""
Debug what's actually stored in the TEST namespace.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def debug_namespace_content():
    """Debug what's actually stored in the TEST namespace."""
    print("Debugging TEST Namespace Content...")
    print("=" * 40)
    
    # Test different queries to see what's in TEST namespace
    queries = [
        "What is my name?",
        "What documents are available?",
        "Tell me everything you know",
        "What information do you have?",
        "What can you tell me about the user?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        
        query_data = {
            "namespace": "TEST",
            "query": query,
            "k": 5  # Get more results
        }
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                context = result.get('context', [])
                
                print(f"Answer: {answer}")
                print(f"Context items: {len(context)}")
                
                # Show full context
                for i, ctx in enumerate(context):
                    print(f"Context {i+1}: {ctx}")
                    print()
            else:
                print(f"FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_namespace_content()
