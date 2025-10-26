#!/usr/bin/env python3
"""
Test conversational responses to ensure they're working properly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_conversational_responses():
    """Test various conversational queries."""
    print("Testing Conversational Responses...")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What is this system about?",
        "How does RAGFlow work?",
        "What can I do with this system?",
        "Tell me about the features",
        "What documents does it support?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        print("-" * 40)
        
        query_data = {
            "namespace": "demo",
            "query": query,
            "k": 3
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=60)
            end_time = time.time()
            
            duration = end_time - start_time
            print(f"Response time: {duration:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                
                print(f"Answer length: {len(answer)}")
                print(f"Answer preview: {answer[:150]}...")
                
                # Check if it's conversational
                conversational_indicators = [
                    "based on", "here's", "the system", "you can", "it supports",
                    "this system", "ragflow", "documents", "vector"
                ]
                
                is_conversational = any(indicator in answer.lower() for indicator in conversational_indicators)
                
                if is_conversational:
                    print("SUCCESS: Response is conversational")
                else:
                    print("WARNING: Response might not be conversational")
                
                # Check for error messages
                if "trouble processing" in answer.lower() or "error" in answer.lower():
                    print("ERROR: Still getting error fallback")
                else:
                    print("SUCCESS: No error fallback detected")
                    
            else:
                print(f"FAILED: Status {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("ERROR: Query timed out")
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("CONVERSATIONAL RESPONSE TEST COMPLETED!")

if __name__ == "__main__":
    test_conversational_responses()
