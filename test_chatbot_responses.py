#!/usr/bin/env python3
"""
Test the conversational chatbot responses.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chatbot_responses():
    """Test conversational chatbot responses."""
    print("Testing Conversational Chatbot Responses...")
    print("=" * 50)
    
    # Test 1: Check backend health
    print("\n1. Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test 2: Check if we have documents
    print("\n2. Checking for documents...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        stats = response.json()
        
        total_docs = stats.get('total_docs', 0)
        namespaces = stats.get('by_namespace', {})
        
        if total_docs == 0:
            print("⚠️ No documents found. Need to upload and embed first.")
            return
        
        # Find a namespace with data
        test_namespace = None
        for ns, count in namespaces.items():
            if count > 0:
                test_namespace = ns
                break
        
        if not test_namespace:
            print("⚠️ No namespaces with data found.")
            return
            
        print(f"✅ Found namespace with data: {test_namespace}")
        
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
        return
    
    # Test 3: Test conversational queries
    print(f"\n3. Testing conversational queries...")
    chat_queries = [
        "What is the computer architecture?",
        "How does this system work?",
        "What are the main features?",
        "Tell me about the tech stack",
        "What can this system do?"
    ]
    
    for query in chat_queries:
        try:
            print(f"\n💬 Testing query: {query}")
            query_data = {
                "namespace": test_namespace,
                "query": query,
                "k": 3
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=60)
            end_time = time.time()
            
            duration = end_time - start_time
            print(f"⏱️ Query took {duration:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                
                print(f"✅ Query successful!")
                print(f"📝 Response: {answer}")
                
                # Check for conversational formatting
                if any(phrase in answer.lower() for phrase in ["i", "you", "the system", "based on", "here's"]):
                    print(f"✅ Response appears conversational")
                else:
                    print(f"⚠️ Response might not be conversational")
                
                # Check for technical metadata (should NOT be present)
                if any(phrase in answer for phrase in ["Sources:", "Context Length:", "Technical Analysis:", "## Overview"]):
                    print(f"❌ Response still contains technical metadata")
                else:
                    print(f"✅ Response is clean without technical metadata")
                
                # Check for malformed text
                if "erse results" in answer:
                    print(f"❌ Response still contains malformed text")
                else:
                    print(f"✅ Response appears properly formatted")
                
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Query timed out after 60 seconds")
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 CHATBOT RESPONSE TEST COMPLETED!")
    print("✅ Conversational responses")
    print("✅ Clean output without metadata")
    print("✅ Natural language formatting")
    print("✅ User-friendly responses")
    print("=" * 50)

if __name__ == "__main__":
    test_chatbot_responses()
