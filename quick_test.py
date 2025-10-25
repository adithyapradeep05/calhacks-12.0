#!/usr/bin/env python3
"""
Quick test to verify backend is working.
"""

import requests
import json

def quick_test():
    """Quick test of the backend."""
    print("Quick Backend Test...")
    
    try:
        # Test health
        response = requests.get("http://localhost:8000/stats", timeout=5)
        print(f"Health check: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"Stats: {stats}")
            
            # Test a simple query if we have data
            if stats.get('total_docs', 0) > 0:
                print("\nTesting query...")
                query_data = {
                    "namespace": "demo",
                    "query": "What is RAGFlow?",
                    "k": 2
                }
                
                response = requests.post("http://localhost:8000/query", json=query_data, timeout=10)
                print(f"Query response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Answer: {result.get('answer', 'No answer')[:100]}...")
                else:
                    print(f"Query error: {response.text}")
            else:
                print("No documents found. Need to upload first.")
        else:
            print(f"Backend not responding: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()
