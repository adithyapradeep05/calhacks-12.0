#!/usr/bin/env python3
"""
Test backend status and see what's happening.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_backend_status():
    """Test backend status and responses."""
    print("Testing Backend Status...")
    print("=" * 40)
    
    # Test query
    query_data = {
        "namespace": "test",
        "query": "What is the technical architecture?",
        "k": 3
    }
    
    try:
        print("Sending query...")
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            print(f"SUCCESS: Query successful")
            print(f"Answer: {answer}")
            
            # Check response format
            if "Based on the documents, here's what I can tell you:" in answer:
                print("WARNING: Using fallback response (Claude error)")
            elif "I'm not able to process your question properly" in answer:
                print("WARNING: Claude client not available")
            elif "I couldn't find any relevant information" in answer:
                print("WARNING: No context available")
            else:
                print("SUCCESS: Got proper Claude response")
                
        else:
            print(f"FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_backend_status()
