#!/usr/bin/env python3
"""
Test the new RAGFlow prompt template.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_new_prompt_template():
    """Test the new prompt template."""
    print("Testing New RAGFlow Prompt Template...")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What is the technical architecture?",
        "What documents are available?",
        "What is my name?",
        "How does the system work?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        query_data = {
            "namespace": "test",
            "query": query,
            "k": 4
        }
        
        try:
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                
                print(f"Response:\n{answer}")
                
                # Check for new format
                if "**Answer:**" in answer and "**Sources:**" in answer:
                    print("✅ SUCCESS: Using new RAGFlow format")
                elif "Based on the documents, here's what I can tell you:" in answer:
                    print("❌ WARNING: Still using old format")
                else:
                    print("⚠️ INFO: Different format detected")
                
                # Check for citations
                if "[S" in answer:
                    print("✅ SUCCESS: Includes source citations")
                else:
                    print("⚠️ INFO: No source citations found")
                    
            else:
                print(f"FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("NEW PROMPT TEMPLATE TEST COMPLETED!")

if __name__ == "__main__":
    test_new_prompt_template()
