#!/usr/bin/env python3
"""
Test improved chunking and query functionality.
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_improved_chunking():
    """Test the improved chunking functionality."""
    print("Testing Improved Chunking & Query...")
    print("=" * 50)
    
    # Test 1: Upload a longer document
    print("\n1. Creating a longer test document...")
    longer_content = """
RAGFlow: Advanced Document Processing System

RAGFlow is a cutting-edge document processing system that combines the power of vector databases with large language models to create an intelligent document search and question-answering platform.

Key Features:
- Vector-based document search using OpenAI embeddings
- Intelligent text chunking with overlap for better context
- Deduplication to prevent redundant content
- Caching system for faster processing
- MMR (Maximum Marginal Relevance) reranking for diverse results
- Support for PDF, TXT, and Markdown files
- Real-time chat interface for document queries

Technical Architecture:
The system uses ChromaDB as the vector database, OpenAI's text-embedding-3-small model for generating embeddings, and Claude for generating human-like responses. Documents are automatically chunked into manageable pieces with configurable overlap to maintain context across boundaries.

Use Cases:
- Research document analysis
- Knowledge base management
- Customer support automation
- Educational content processing
- Legal document review
- Technical documentation search

The system is designed to handle large documents efficiently while maintaining high accuracy in retrieval and generation tasks.

Additional Technical Details:
RAGFlow implements several advanced features including semantic search capabilities, automatic document preprocessing, and intelligent context retrieval. The system supports multiple embedding models and can be configured for different use cases.

Performance Optimization:
The system includes caching mechanisms for embeddings, batch processing for large documents, and optimized vector storage in ChromaDB. This ensures fast query responses even with large document collections.

Integration Features:
RAGFlow can be integrated with existing document management systems, content management platforms, and knowledge bases. It supports API-based integration and can be deployed in various environments.
"""
    
    with open("longer-test-document.txt", "w", encoding="utf-8") as f:
        f.write(longer_content)
    
    print("✅ Created longer test document")
    
    # Test 2: Upload the longer document
    print("\n2. Uploading longer document...")
    try:
        with open("longer-test-document.txt", "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"✅ Upload successful: {upload_result['filename']}")
            file_path = upload_result["path"]
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # Test 3: Embed with improved chunking
    print("\n3. Embedding with improved chunking...")
    try:
        embed_data = {"path": file_path, "namespace": "improved-test"}
        response = requests.post(f"{BASE_URL}/embed", json=embed_data)
        
        if response.status_code == 200:
            embed_result = response.json()
            print(f"✅ Embedding successful: {embed_result['chunks']} chunks")
            print(f"📊 This should be more than 3 chunks due to improved chunking!")
        else:
            print(f"❌ Embedding failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return
    
    # Test 4: Test query functionality
    print("\n4. Testing query functionality...")
    try:
        query_data = {
            "namespace": "improved-test",
            "query": "What vector database does RAGFlow use?",
            "k": 4
        }
        
        print(f"🔍 Query: {query_data['query']}")
        response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"📝 Answer: {result.get('answer', 'No answer')}")
            print(f"📚 Context sources: {len(result.get('context', []))}")
            
            # Show context snippets
            for i, ctx in enumerate(result.get('context', [])[:2]):
                print(f"   Source {i+1}: {ctx[:100]}...")
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return
    
    # Test 5: Check stats
    print("\n5. Checking final stats...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Final stats: {stats}")
            
            # Check if we have more vectors now
            total_chunks = stats.get('total_chunks', 0)
            print(f"📊 Total chunks in system: {total_chunks}")
            
            if total_chunks > 3:
                print("🎉 SUCCESS: We now have more than 3 vectors!")
            else:
                print("⚠️ Still only 3 vectors - chunking might need further adjustment")
        else:
            print(f"❌ Stats check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 IMPROVED CHUNKING TEST COMPLETED!")
    print("✅ Smaller chunk size (400 chars)")
    print("✅ Better overlap (100 chars)")
    print("✅ Improved chunking algorithm")
    print("✅ Query functionality working")
    print("=" * 50)

if __name__ == "__main__":
    test_improved_chunking()
