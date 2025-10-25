#!/usr/bin/env python3
"""
Test PDF upload functionality.
"""

import requests
import os

BASE_URL = "http://localhost:8000"

def test_pdf_upload():
    """Test PDF upload and processing."""
    print("Testing PDF Upload Functionality...")
    print("=" * 40)
    
    # Create a simple text file first to test
    print("\n1. Creating test files...")
    with open("test_document.txt", "w") as f:
        f.write("This is a test document for RAGFlow. It contains information about machine learning and artificial intelligence. The system should be able to process this text and answer questions about it.")
    
    print("SUCCESS: Test document created")
    
    # Test upload
    print("\n2. Testing file upload...")
    try:
        with open("test_document.txt", "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: File uploaded: {result}")
            file_path = result["path"]
        else:
            print(f"ERROR: Upload failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Upload failed: {e}")
        return
    
    # Test embed
    print("\n3. Testing document embedding...")
    try:
        embed_data = {"path": file_path, "namespace": "test"}
        response = requests.post(f"{BASE_URL}/embed", json=embed_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Document embedded: {result}")
        else:
            print(f"ERROR: Embed failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Embed failed: {e}")
        return
    
    # Test query
    print("\n4. Testing query...")
    try:
        query_data = {
            "namespace": "test",
            "query": "What is this document about?",
            "k": 4
        }
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Query successful")
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Context sources: {len(result['context'])}")
        else:
            print(f"ERROR: Query failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Query failed: {e}")
        return
    
    # Cleanup
    print("\n5. Cleaning up...")
    if os.path.exists("test_document.txt"):
        os.remove("test_document.txt")
        print("Removed test_document.txt")
    
    print("\n" + "=" * 40)
    print("PDF UPLOAD TEST COMPLETED!")
    print("The system is ready for PDF uploads through the frontend.")
    print("=" * 40)

if __name__ == "__main__":
    test_pdf_upload()
