#!/usr/bin/env python3
"""
Simple backend test without Unicode characters.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def simple_backend_test():
    """Simple backend test."""
    print("Simple Backend Test")
    print("=" * 30)
    
    try:
        # Check stats
        print("1. Checking stats...")
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print("SUCCESS: Stats endpoint working")
            print(f"Total docs: {stats.get('total_docs', 0)}")
            print(f"Namespaces: {stats.get('by_namespace', {})}")
        else:
            print(f"FAILED: Stats {response.status_code}")
            
        # Test query
        print("\n2. Testing query...")
        query_data = {
            "namespace": "demo",
            "query": "What is my name?",
            "k": 1
        }
        
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            print("SUCCESS: Query endpoint working")
            print(f"Response: {answer}")
            
            # Check response type
            if "Based on the documents, here's what I can tell you:" in answer:
                print("INFO: Hitting fallback response - Claude error")
            elif "I'm not able to process your question properly" in answer:
                print("INFO: Claude client not available")
            elif "I couldn't find any relevant information" in answer:
                print("INFO: No context available")
            else:
                print("SUCCESS: Got proper Claude response")
        else:
            print(f"FAILED: Query {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    simple_backend_test()
