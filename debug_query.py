#!/usr/bin/env python3
"""
Debug query issue.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def debug_query():
    """Debug the query issue."""
    print("Debugging query issue...")
    
    # Test stats first
    print("\n1. Testing stats...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"SUCCESS: Stats: {stats}")
        else:
            print(f"ERROR: Stats failed: {response.status_code}")
            return
    except Exception as e:
        print(f"ERROR: Stats failed: {e}")
        return
    
    # Test a simple query
    print("\n2. Testing simple query...")
    try:
        query_data = {
            "namespace": "test",
            "query": "test",
            "k": 1
        }
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
    except Exception as e:
        print(f"ERROR: Query failed: {e}")

if __name__ == "__main__":
    debug_query()
