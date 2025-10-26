#!/usr/bin/env python3
"""
Test the fixed conversational responses.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_fixed_responses():
    """Test the fixed conversational responses."""
    print("Testing Fixed Conversational Responses...")
    print("=" * 50)
    
    # Test queries that should work well
    test_queries = [
        "What is my name?",
        "What is this system about?",
        "How does RAGFlow work?",
        "What documents does it support?",
        "Tell me about the features"
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
                print(f"Answer:\n{answer}")
                
                # Check for conversational indicators
                conversational_indicators = [
                    "based on", "here's", "the system", "you can", "it supports",
                    "this system", "ragflow", "documents", "vector", "i found",
                    "i can tell you", "i hope this", "i couldn't find"
                ]
                
                is_conversational = any(indicator in answer.lower() for indicator in conversational_indicators)
                
                if is_conversational:
                    print("SUCCESS: Response is conversational")
                else:
                    print("WARNING: Response might not be conversational")
                
                # Check for old technical formatting (should NOT be present)
                technical_indicators = [
                    "based on the retrieved context",
                    "key points:",
                    "sources:",
                    "context length:",
                    "information extracted from",
                    "fallback response due to an error"
                ]
                
                has_technical_formatting = any(indicator in answer.lower() for indicator in technical_indicators)
                
                if has_technical_formatting:
                    print("ERROR: Still has technical formatting")
                else:
                    print("SUCCESS: No technical formatting detected")
                
                # Check for malformed text (should NOT be present)
                malformed_indicators = [
                    "erse results",
                    "erse",
                    "malformed",
                    "garbled"
                ]
                
                has_malformed_text = any(indicator in answer.lower() for indicator in malformed_indicators)
                
                if has_malformed_text:
                    print("ERROR: Still has malformed text")
                else:
                    print("SUCCESS: No malformed text detected")
                    
            else:
                print(f"FAILED: Status {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("ERROR: Query timed out")
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("FIXED RESPONSE TEST COMPLETED!")
    print("Expected Results:")
    print("✅ Conversational responses")
    print("✅ No technical formatting")
    print("✅ No malformed text")
    print("✅ Clean, helpful answers")
    print("=" * 50)

if __name__ == "__main__":
    test_fixed_responses()
