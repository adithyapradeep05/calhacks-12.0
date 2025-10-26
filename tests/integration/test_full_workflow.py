#!/usr/bin/env python3
"""
Full Workflow Integration Test
Tests the complete RAGFlow system end-to-end
"""

import asyncio
import time
import json
import os
import requests
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TestResult:
    """Test result data"""
    test_name: str
    passed: bool
    duration_ms: int
    error: str = None
    details: Dict[str, Any] = None

class FullWorkflowTest:
    """Comprehensive end-to-end test suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.test_documents = self._create_test_documents()
    
    def _create_test_documents(self) -> List[Dict[str, Any]]:
        """Create test documents for comprehensive testing"""
        return [
            {
                "filename": "legal_contract.pdf",
                "content": "This software license agreement governs the use of our proprietary software. By installing or using the software, you agree to be bound by the terms and conditions set forth herein. This agreement is legally binding and enforceable under applicable law.",
                "expected_category": "legal"
            },
            {
                "filename": "api_documentation.md",
                "content": "API Documentation: The /api/v1/users endpoint returns a list of user objects. Authentication is required via Bearer token. Response format is JSON with pagination support. Rate limiting: 100 requests per minute.",
                "expected_category": "technical"
            },
            {
                "filename": "financial_report.pdf",
                "content": "Q3 2024 Financial Report: Revenue increased by 15% compared to Q2, reaching $2.3M. Operating expenses were $1.8M. Net profit margin improved to 12%. Budget allocation for next quarter is $3.5M.",
                "expected_category": "financial"
            },
            {
                "filename": "employee_handbook.pdf",
                "content": "Employee Handbook: All employees are entitled to 15 days of paid vacation annually. Health insurance coverage begins on the first day of employment. Performance reviews are conducted quarterly with 360-degree feedback.",
                "expected_category": "hr"
            },
            {
                "filename": "meeting_notes.txt",
                "content": "Meeting Notes - Weekly Standup: Discussed project progress, upcoming deadlines, and resource allocation. Action items: Complete user authentication by Friday, review code with team lead. Next meeting scheduled for Friday 2 PM.",
                "expected_category": "general"
            }
        ]
    
    def _record_result(self, test_name: str, passed: bool, duration_ms: int, 
                      error: str = None, details: Dict[str, Any] = None):
        """Record test result"""
        result = TestResult(
            test_name=test_name,
            passed=passed,
            duration_ms=duration_ms,
            error=error,
            details=details or {}
        )
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status} ({duration_ms}ms)")
        if error:
            print(f"      Error: {error}")
    
    def test_health_check(self) -> bool:
        """Test system health check"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            duration_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                health_data = response.json()
                services = health_data.get("services", {})
                
                # Check critical services
                critical_services = ["redis", "supabase", "chromadb", "claude", "cache", "classifier"]
                healthy_services = sum(1 for service in critical_services if services.get(service) == "✅")
                
                self._record_result(
                    "Health Check",
                    healthy_services >= 4,  # At least 4/6 services healthy
                    duration_ms,
                    details={"healthy_services": healthy_services, "total_services": len(critical_services)}
                )
                return healthy_services >= 4
            else:
                self._record_result("Health Check", False, duration_ms, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._record_result("Health Check", False, duration_ms, str(e))
            return False
    
    def test_document_upload_and_classification(self) -> List[str]:
        """Test document upload and classification"""
        print("\n📄 Testing Document Upload and Classification...")
        document_ids = []
        
        for i, doc in enumerate(self.test_documents):
            start_time = time.time()
            try:
                # Create a temporary file
                temp_filename = f"test_{i}_{doc['filename']}"
                with open(temp_filename, 'w') as f:
                    f.write(doc['content'])
                
                # Upload file
                with open(temp_filename, 'rb') as f:
                    files = {'file': (doc['filename'], f, 'text/plain')}
                    response = requests.post(f"{self.base_url}/upload", files=files, timeout=30)
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    upload_data = response.json()
                    document_id = upload_data.get('document_id')
                    category = upload_data.get('category')
                    confidence = upload_data.get('confidence', 0)
                    
                    # Check classification accuracy
                    correct_category = category == doc['expected_category']
                    high_confidence = confidence >= 0.7
                    
                    document_ids.append(document_id)
                    
                    self._record_result(
                        f"Upload {doc['filename']}",
                        correct_category and high_confidence,
                        duration_ms,
                        details={
                            "expected_category": doc['expected_category'],
                            "actual_category": category,
                            "confidence": confidence,
                            "document_id": document_id
                        }
                    )
                else:
                    self._record_result(f"Upload {doc['filename']}", False, duration_ms, f"HTTP {response.status_code}")
                
                # Clean up temp file
                os.remove(temp_filename)
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                self._record_result(f"Upload {doc['filename']}", False, duration_ms, str(e))
        
        return document_ids
    
    def test_document_embedding(self, document_ids: List[str]) -> bool:
        """Test document embedding"""
        print("\n🧠 Testing Document Embedding...")
        success_count = 0
        
        for doc_id in document_ids:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/embed",
                    json={"document_id": doc_id, "namespace": "default"},
                    timeout=60
                )
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    embed_data = response.json()
                    chunks_processed = embed_data.get('chunks_processed', 0)
                    
                    success = chunks_processed > 0
                    if success:
                        success_count += 1
                    
                    self._record_result(
                        f"Embed {doc_id[:8]}...",
                        success,
                        duration_ms,
                        details={"chunks_processed": chunks_processed}
                    )
                else:
                    self._record_result(f"Embed {doc_id[:8]}...", False, duration_ms, f"HTTP {response.status_code}")
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                self._record_result(f"Embed {doc_id[:8]}...", False, duration_ms, str(e))
        
        return success_count >= len(document_ids) * 0.8  # 80% success rate
    
    def test_query_routing_and_response(self) -> bool:
        """Test query routing and response generation"""
        print("\n🔍 Testing Query Routing and Response...")
        test_queries = [
            {
                "query": "What are the terms of the software license?",
                "expected_category": "legal"
            },
            {
                "query": "How do I authenticate with the API?",
                "expected_category": "technical"
            },
            {
                "query": "What was the Q3 revenue?",
                "expected_category": "financial"
            },
            {
                "query": "What are the vacation policies?",
                "expected_category": "hr"
            },
            {
                "query": "What was discussed in the meeting?",
                "expected_category": "general"
            }
        ]
        
        success_count = 0
        
        for test_query in test_queries:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/query",
                    json={
                        "query": test_query["query"],
                        "namespace": "default",
                        "max_results": 5
                    },
                    timeout=30
                )
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    query_data = response.json()
                    answer = query_data.get('answer', '')
                    category = query_data.get('category', '')
                    sources = query_data.get('sources', 0)
                    processing_time = query_data.get('processing_time_ms', 0)
                    
                    # Check response quality
                    has_answer = len(answer) > 10
                    correct_routing = category == test_query["expected_category"]
                    has_sources = sources > 0
                    fast_response = processing_time < 5000  # < 5 seconds
                    
                    success = has_answer and has_sources and fast_response
                    if success:
                        success_count += 1
                    
                    self._record_result(
                        f"Query: {test_query['query'][:30]}...",
                        success,
                        duration_ms,
                        details={
                            "expected_category": test_query["expected_category"],
                            "actual_category": category,
                            "sources": sources,
                            "processing_time_ms": processing_time,
                            "answer_length": len(answer)
                        }
                    )
                else:
                    self._record_result(f"Query: {test_query['query'][:30]}...", False, duration_ms, f"HTTP {response.status_code}")
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                self._record_result(f"Query: {test_query['query'][:30]}...", False, duration_ms, str(e))
        
        return success_count >= len(test_queries) * 0.8  # 80% success rate
    
    def test_cache_performance(self) -> bool:
        """Test cache performance"""
        print("\n⚡ Testing Cache Performance...")
        
        # Test query caching
        test_query = "What are the software license terms?"
        cache_hits = 0
        total_queries = 5
        
        for i in range(total_queries):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/query",
                    json={"query": test_query, "namespace": "default"},
                    timeout=30
                )
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    # First query should be slow, subsequent should be fast (cached)
                    if i == 0:
                        expected_slow = duration_ms > 1000  # First query should be > 1s
                        self._record_result(
                            f"Cache Test - First Query",
                            expected_slow,
                            duration_ms,
                            details={"query_number": i + 1}
                        )
                    else:
                        expected_fast = duration_ms < 500  # Cached queries should be < 500ms
                        if expected_fast:
                            cache_hits += 1
                        self._record_result(
                            f"Cache Test - Query {i + 1}",
                            expected_fast,
                            duration_ms,
                            details={"query_number": i + 1, "cached": expected_fast}
                        )
                else:
                    self._record_result(f"Cache Test - Query {i + 1}", False, duration_ms, f"HTTP {response.status_code}")
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                self._record_result(f"Cache Test - Query {i + 1}", False, duration_ms, str(e))
        
        cache_hit_rate = cache_hits / (total_queries - 1) if total_queries > 1 else 0
        return cache_hit_rate >= 0.5  # 50% cache hit rate
    
    def test_system_statistics(self) -> bool:
        """Test system statistics endpoint"""
        print("\n📊 Testing System Statistics...")
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            duration_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                stats_data = response.json()
                
                # Check required fields
                has_documents = "total_documents" in stats_data
                has_chunks = "total_chunks" in stats_data
                has_categories = "categories" in stats_data
                has_cache_stats = "cache_stats" in stats_data
                
                success = has_documents and has_chunks and has_categories and has_cache_stats
                
                self._record_result(
                    "System Statistics",
                    success,
                    duration_ms,
                    details={
                        "total_documents": stats_data.get("total_documents", 0),
                        "total_chunks": stats_data.get("total_chunks", 0),
                        "categories": stats_data.get("categories", {}),
                        "has_cache_stats": has_cache_stats
                    }
                )
                return success
            else:
                self._record_result("System Statistics", False, duration_ms, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._record_result("System Statistics", False, duration_ms, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🚀 Starting Full Workflow Integration Tests")
        print("=" * 60)
        
        overall_start_time = time.time()
        
        # Test 1: Health Check
        print("\n🏥 Testing System Health...")
        health_ok = self.test_health_check()
        
        if not health_ok:
            print("❌ System health check failed. Stopping tests.")
            return self._generate_report(overall_start_time)
        
        # Test 2: Document Upload and Classification
        document_ids = self.test_document_upload_and_classification()
        
        # Test 3: Document Embedding
        if document_ids:
            embedding_ok = self.test_document_embedding(document_ids)
        else:
            embedding_ok = False
        
        # Test 4: Query Routing and Response
        query_ok = self.test_query_routing_and_response()
        
        # Test 5: Cache Performance
        cache_ok = self.test_cache_performance()
        
        # Test 6: System Statistics
        stats_ok = self.test_system_statistics()
        
        return self._generate_report(overall_start_time)
    
    def _generate_report(self, start_time: float) -> Dict[str, Any]:
        """Generate test report"""
        total_duration = int((time.time() - start_time) * 1000)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Duration: {total_duration}ms")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"   {status} {result.test_name} ({result.duration_ms}ms)")
            if result.error:
                print(f"      Error: {result.error}")
        
        # Success criteria check
        print("\n🎯 Success Criteria:")
        criteria_met = {
            "Health Check": any(r.passed for r in self.results if "Health Check" in r.test_name),
            "Document Upload": any(r.passed for r in self.results if "Upload" in r.test_name),
            "Document Embedding": any(r.passed for r in self.results if "Embed" in r.test_name),
            "Query Routing": any(r.passed for r in self.results if "Query:" in r.test_name),
            "Cache Performance": any(r.passed for r in self.results if "Cache Test" in r.test_name),
            "System Statistics": any(r.passed for r in self.results if "System Statistics" in r.test_name)
        }
        
        for criterion, met in criteria_met.items():
            status = "✅" if met else "❌"
            print(f"   {status} {criterion}")
        
        overall_success = success_rate >= 80 and all(criteria_met.values())
        
        print(f"\n🎉 Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
        
        # Save results
        report = {
            "timestamp": time.time(),
            "total_duration_ms": total_duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "overall_success": overall_success,
            "criteria_met": criteria_met,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "error": r.error,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        with open("integration_test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Results saved to integration_test_results.json")
        
        return report

def main():
    """Main test function"""
    tester = FullWorkflowTest()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if report["overall_success"] else 1)

if __name__ == "__main__":
    main()
