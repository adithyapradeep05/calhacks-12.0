#!/usr/bin/env python3
"""
Supabase Schema Verification Script
Tests database connection, schema, and operations
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from managers.supabase_manager import supabase_manager

def test_connection():
    """Test Supabase connection"""
    print("🔌 Testing Supabase Connection...")
    
    health = supabase_manager.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    
    if health.get('status') == 'connected':
        print("   ✅ Supabase connection successful")
        return True
    else:
        print(f"   ❌ Supabase connection failed: {health.get('error', 'Unknown error')}")
        return False

def test_document_operations():
    """Test document CRUD operations"""
    print("\n📄 Testing Document Operations...")
    
    # Test document storage
    test_doc_id = f"test_doc_{int(time.time())}"
    success = supabase_manager.store_document(
        document_id=test_doc_id,
        filename="test_document.txt",
        category="test",
        storage_path="/test/path",
        file_size=1024,
        confidence=0.95,
        namespace="test_namespace",
        metadata={"test": "data"}
    )
    
    if success:
        print("   ✅ Document storage successful")
    else:
        print("   ❌ Document storage failed")
        return False
    
    # Test document retrieval
    doc = supabase_manager.get_document(test_doc_id)
    if doc:
        print("   ✅ Document retrieval successful")
        print(f"   📋 Retrieved: {doc['filename']} (category: {doc['category']})")
    else:
        print("   ❌ Document retrieval failed")
        return False
    
    # Test category retrieval
    category = supabase_manager.get_document_category(test_doc_id)
    if category == "test":
        print("   ✅ Category retrieval successful")
    else:
        print(f"   ❌ Category retrieval failed: expected 'test', got '{category}'")
        return False
    
    return True

def test_query_logging():
    """Test query logging functionality"""
    print("\n📊 Testing Query Logging...")
    
    # Test query log storage
    success = supabase_manager.log_query(
        query="What is the test data?",
        category="test",
        response_time=150,
        cache_hit=True,
        namespace="test_namespace"
    )
    
    if success:
        print("   ✅ Query logging successful")
    else:
        print("   ❌ Query logging failed")
        return False
    
    # Test query stats retrieval
    stats = supabase_manager.get_query_stats(category="test", namespace="test_namespace")
    if stats and stats.get("total_queries", 0) > 0:
        print("   ✅ Query stats retrieval successful")
        print(f"   📈 Stats: {stats}")
    else:
        print("   ❌ Query stats retrieval failed")
        return False
    
    return True

def test_category_stats():
    """Test category statistics"""
    print("\n📈 Testing Category Statistics...")
    
    # Test category stats update with a unique category
    unique_category = f"test_stats_{int(time.time())}"
    success = supabase_manager.update_category_stats(
        category=unique_category,
        doc_count=1,
        avg_response_time=150.0,
        total_queries=1,
        cache_hit_rate=100.0
    )
    
    if success:
        print("   ✅ Category stats update successful")
    else:
        print("   ❌ Category stats update failed")
        return False
    
    # Test category stats retrieval
    stats = supabase_manager.get_category_stats()
    if unique_category in stats:
        print("   ✅ Category stats retrieval successful")
        print(f"   📊 {unique_category} stats: {stats[unique_category]}")
    else:
        print("   ❌ Category stats retrieval failed")
        return False
    
    return True

def test_embedding_metadata():
    """Test embedding metadata operations"""
    print("\n🧠 Testing Embedding Metadata...")
    
    # First create a document that we can reference
    test_doc_id = f"embed_test_{int(time.time())}"
    
    # Store the document first
    doc_success = supabase_manager.store_document(
        document_id=test_doc_id,
        filename="embedding_test_doc.txt",
        category="test_embedding",
        storage_path="/test/embedding/path",
        file_size=512,
        confidence=0.9,
        namespace="test_namespace"
    )
    
    if not doc_success:
        print("   ❌ Failed to create test document for embedding metadata")
        return False
    
    # Test embedding metadata storage
    success = supabase_manager.store_embedding_metadata(
        document_id=test_doc_id,
        chunk_count=5,
        embedding_model="text-embedding-3-small",
        processing_time=250
    )
    
    if success:
        print("   ✅ Embedding metadata storage successful")
    else:
        print("   ❌ Embedding metadata storage failed")
        return False
    
    # Test embedding metadata retrieval
    metadata = supabase_manager.get_embedding_metadata(test_doc_id)
    if metadata and metadata.get("chunk_count") == 5:
        print("   ✅ Embedding metadata retrieval successful")
        print(f"   🔍 Metadata: {metadata}")
    else:
        print("   ❌ Embedding metadata retrieval failed")
        return False
    
    return True

def test_schema_verification():
    """Verify that required tables exist"""
    print("\n🗄️ Testing Schema Verification...")
    
    # This would require direct SQL queries to check table existence
    # For now, we'll test by trying operations on each table
    print("   📋 Testing table accessibility...")
    
    # Test documents table
    try:
        docs = supabase_manager.get_documents_by_category("test")
        print("   ✅ Documents table accessible")
    except Exception as e:
        print(f"   ❌ Documents table error: {e}")
        return False
    
    # Test query_logs table
    try:
        stats = supabase_manager.get_query_stats()
        print("   ✅ Query logs table accessible")
    except Exception as e:
        print(f"   ❌ Query logs table error: {e}")
        return False
    
    # Test category_stats table
    try:
        cat_stats = supabase_manager.get_category_stats()
        print("   ✅ Category stats table accessible")
    except Exception as e:
        print(f"   ❌ Category stats table error: {e}")
        return False
    
    return True

def main():
    """Run all Supabase schema tests"""
    print("🧪 RAGFlow Supabase Schema Verification")
    print("=" * 50)
    
    tests = [
        ("Connection", test_connection),
        ("Document Operations", test_document_operations),
        ("Query Logging", test_query_logging),
        ("Category Statistics", test_category_stats),
        ("Embedding Metadata", test_embedding_metadata),
        ("Schema Verification", test_schema_verification)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Supabase schema tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
