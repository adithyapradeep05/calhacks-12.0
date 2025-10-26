#!/usr/bin/env python3
"""
Test the 'tet' namespace after the embedding fix.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_tet_after_fix():
    """Test the 'tet' namespace after the embedding fix."""
    print("Testing 'tet' Namespace After Fix...")
    print("=" * 50)
    
    # Test queries
    queries = [
        "What is my name?",
        "What documents are available?",
        "Tell me about the user",
        "What information do you have?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        
        query_data = {
            "namespace": "tet",
            "query": query,
            "k": 5
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
                    print("SUCCESS: Name found!")
                else:
                    print("INFO: No name found")
                
                # Check for conversational format
                if "Based on the documents, here's what I can tell you:" in answer:
                    print("WARNING: Still using old technical format")
                else:
                    print("SUCCESS: Using conversational format")
                    
                # Show context previews
                for i, ctx in enumerate(context[:2]):
                    print(f"Context {i+1}: {ctx[:80]}...")
            else:
                print(f"FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_tet_after_fix()
