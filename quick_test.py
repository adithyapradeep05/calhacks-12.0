#!/usr/bin/env python3
"""
Quick test to verify the backend is working with conversational responses.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def quick_test():
    """Quick test of the conversational responses."""
    print("Quick Test - Conversational Responses")
    print("=" * 40)
    
    # Simple test query
    query_data = {
        "namespace": "demo",
        "query": "What is my name?",
        "k": 3
    }
    
    try:
        print("Sending query...")
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            print(f"SUCCESS! Response received:")
            print(f"Answer: {answer}")
            
            # Check if it's conversational
            if any(phrase in answer.lower() for phrase in ["based on", "here's", "i can tell you", "i found"]):
                print("✅ Response is conversational")
            else:
                print("⚠️ Response might not be conversational")
            
            # Check for old technical format
            if any(phrase in answer.lower() for phrase in ["based on the retrieved context", "key points:", "sources:"]):
                print("❌ Still has technical formatting")
            else:
                print("✅ No technical formatting")
                
            # Check for malformed text
            if "erse results" in answer.lower():
                print("❌ Still has malformed text")
            else:
                print("✅ No malformed text")
                
        else:
            print(f"FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    quick_test()