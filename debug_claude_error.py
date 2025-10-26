#!/usr/bin/env python3
"""
Debug Claude error to see what's happening.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def debug_claude_error():
    """Debug the Claude error."""
    print("Debugging Claude Error...")
    print("=" * 40)
    
    # Test query
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
            context = result.get('context', [])
            
            print(f"Answer: {answer}")
            print(f"Context items: {len(context)}")
            
            # Check if it's the fallback response
            if "Based on the documents, here's what I can tell you:" in answer:
                print("❌ Hitting fallback response - Claude error occurred")
            elif "I'm not able to process your question properly" in answer:
                print("❌ Claude client not available")
            elif "I couldn't find any relevant information" in answer:
                print("❌ No context available")
            else:
                print("✅ Got proper Claude response")
                
        else:
            print(f"FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_claude_error()
