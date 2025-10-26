#!/usr/bin/env python3
"""
Load Testing for RAGFlow System
Tests system performance under various load conditions
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import random

@dataclass
class LoadTestResult:
    """Load test result data"""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    max_response_time_ms: float
    min_response_time_ms: float
    requests_per_second: float
    error_rate: float
    errors: List[str]

class LoadTester:
    """Load testing suite for RAGFlow system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[LoadTestResult] = []
        
        # Test queries for load testing
        self.test_queries = [
            "What are the software license terms?",
            "How do I authenticate with the API?",
            "What was the Q3 revenue?",
            "What are the vacation policies?",
            "What was discussed in the meeting?",
            "Explain the system architecture",
            "What are the security requirements?",
            "How does the caching system work?",
            "What are the performance metrics?",
            "Describe the deployment process"
        ]
    
    async def _make_request(self, session: aiohttp.ClientSession, endpoint: str, 
                           method: str = "GET", data: Dict[str, Any] = None) -> Tuple[float, int, str]:
        """Make a single HTTP request and return timing, status, and error"""
        start_time = time.time()
        try:
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    await response.text()
                    duration = (time.time() - start_time) * 1000
                    return duration, response.status, None
            elif method == "POST":
                async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                    await response.text()
                    duration = (time.time() - start_time) * 1000
                    return duration, response.status, None
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return duration, 0, str(e)
    
    async def _concurrent_requests(self, endpoint: str, method: str = "GET", 
                                  data: Dict[str, Any] = None, num_requests: int = 100,
                                  concurrency: int = 10) -> LoadTestResult:
        """Execute concurrent requests and collect metrics"""
        start_time = time.time()
        response_times = []
        errors = []
        successful_requests = 0
        failed_requests = 0
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def make_request_with_semaphore(session):
            async with semaphore:
                duration, status, error = await self._make_request(session, endpoint, method, data)
                response_times.append(duration)
                
                if status == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
                    if error:
                        errors.append(error)
                    else:
                        errors.append(f"HTTP {status}")
        
        async with aiohttp.ClientSession() as session:
            tasks = [make_request_with_semaphore(session) for _ in range(num_requests)]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = p95_response_time = p99_response_time = max_response_time = min_response_time = 0
        
        requests_per_second = num_requests / total_duration if total_duration > 0 else 0
        error_rate = (failed_requests / num_requests) * 100 if num_requests > 0 else 0
        
        return LoadTestResult(
            test_name=f"{method} {endpoint}",
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            max_response_time_ms=max_response_time,
            min_response_time_ms=min_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            errors=errors[:10]  # Keep only first 10 errors
        )
    
    async def test_health_endpoint_load(self) -> LoadTestResult:
        """Test health endpoint under load"""
        print("🏥 Testing health endpoint load...")
        return await self._concurrent_requests("/health", "GET", num_requests=500, concurrency=50)
    
    async def test_query_endpoint_load(self) -> LoadTestResult:
        """Test query endpoint under load"""
        print("🔍 Testing query endpoint load...")
        
        # Use random queries to simulate real usage
        query_data = {
            "query": random.choice(self.test_queries),
            "namespace": "default",
            "max_results": 5
        }
        
        return await self._concurrent_requests("/query", "POST", query_data, num_requests=200, concurrency=20)
    
    async def test_stats_endpoint_load(self) -> LoadTestResult:
        """Test stats endpoint under load"""
        print("📊 Testing stats endpoint load...")
        return await self._concurrent_requests("/stats", "GET", num_requests=300, concurrency=30)
    
    async def test_mixed_workload(self) -> LoadTestResult:
        """Test mixed workload (health, query, stats)"""
        print("🔄 Testing mixed workload...")
        
        start_time = time.time()
        response_times = []
        errors = []
        successful_requests = 0
        failed_requests = 0
        
        async def mixed_request(session):
            # Randomly choose endpoint
            endpoints = [
                ("/health", "GET", None),
                ("/stats", "GET", None),
                ("/query", "POST", {
                    "query": random.choice(self.test_queries),
                    "namespace": "default",
                    "max_results": 5
                })
            ]
            
            endpoint, method, data = random.choice(endpoints)
            duration, status, error = await self._make_request(session, endpoint, method, data)
            
            response_times.append(duration)
            if status == 200:
                successful_requests += 1
            else:
                failed_requests += 1
                if error:
                    errors.append(f"{endpoint}: {error}")
                else:
                    errors.append(f"{endpoint}: HTTP {status}")
        
        async with aiohttp.ClientSession() as session:
            tasks = [mixed_request(session) for _ in range(500)]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            p99_response_time = statistics.quantiles(response_times, n=100)[98]
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = p95_response_time = p99_response_time = max_response_time = min_response_time = 0
        
        requests_per_second = 500 / total_duration if total_duration > 0 else 0
        error_rate = (failed_requests / 500) * 100
        
        return LoadTestResult(
            test_name="Mixed Workload",
            total_requests=500,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            max_response_time_ms=max_response_time,
            min_response_time_ms=min_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            errors=errors[:10]
        )
    
    async def test_sustained_load(self) -> LoadTestResult:
        """Test sustained load over time"""
        print("⏱️ Testing sustained load...")
        
        start_time = time.time()
        response_times = []
        errors = []
        successful_requests = 0
        failed_requests = 0
        
        # Run for 60 seconds
        end_time = start_time + 60
        
        async def sustained_request(session):
            while time.time() < end_time:
                duration, status, error = await self._make_request(session, "/health", "GET")
                response_times.append(duration)
                
                if status == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
                    if error:
                        errors.append(error)
                    else:
                        errors.append(f"HTTP {status}")
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
        
        async with aiohttp.ClientSession() as session:
            # Run 10 concurrent sustained request loops
            tasks = [sustained_request(session) for _ in range(10)]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            p99_response_time = statistics.quantiles(response_times, n=100)[98]
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = p95_response_time = p99_response_time = max_response_time = min_response_time = 0
        
        total_requests = successful_requests + failed_requests
        requests_per_second = total_requests / total_duration if total_duration > 0 else 0
        error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        
        return LoadTestResult(
            test_name="Sustained Load (60s)",
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            max_response_time_ms=max_response_time,
            min_response_time_ms=min_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            errors=errors[:10]
        )
    
    async def run_all_load_tests(self) -> Dict[str, Any]:
        """Run all load tests"""
        print("🚀 Starting Load Testing Suite")
        print("=" * 60)
        
        overall_start_time = time.time()
        
        # Run all load tests
        tests = [
            self.test_health_endpoint_load(),
            self.test_query_endpoint_load(),
            self.test_stats_endpoint_load(),
            self.test_mixed_workload(),
            self.test_sustained_load()
        ]
        
        results = await asyncio.gather(*tests)
        self.results = results
        
        return self._generate_report(overall_start_time)
    
    def _generate_report(self, start_time: float) -> Dict[str, Any]:
        """Generate load test report"""
        total_duration = int((time.time() - start_time) * 1000)
        
        print("\n" + "=" * 60)
        print("📊 LOAD TEST RESULTS")
        print("=" * 60)
        
        # Overall statistics
        total_requests = sum(r.total_requests for r in self.results)
        total_successful = sum(r.successful_requests for r in self.results)
        total_failed = sum(r.failed_requests for r in self.results)
        overall_error_rate = (total_failed / total_requests) * 100 if total_requests > 0 else 0
        
        print(f"Total Requests: {total_requests:,}")
        print(f"Successful: {total_successful:,} ✅")
        print(f"Failed: {total_failed:,} ❌")
        print(f"Overall Error Rate: {overall_error_rate:.2f}%")
        print(f"Total Test Duration: {total_duration}ms")
        
        # Individual test results
        print("\n📋 Individual Test Results:")
        for result in self.results:
            print(f"\n🔍 {result.test_name}")
            print(f"   Requests: {result.total_requests:,}")
            print(f"   Success Rate: {((result.successful_requests / result.total_requests) * 100):.1f}%")
            print(f"   Avg Response Time: {result.avg_response_time_ms:.1f}ms")
            print(f"   P95 Response Time: {result.p95_response_time_ms:.1f}ms")
            print(f"   P99 Response Time: {result.p99_response_time_ms:.1f}ms")
            print(f"   Requests/Second: {result.requests_per_second:.1f}")
            print(f"   Error Rate: {result.error_rate:.2f}%")
            
            if result.errors:
                print(f"   Sample Errors: {result.errors[:3]}")
        
        # Performance criteria
        print("\n🎯 Performance Criteria:")
        criteria = {
            "Health Endpoint < 100ms": any(r.avg_response_time_ms < 100 for r in self.results if "health" in r.test_name.lower()),
            "Query Endpoint < 5s": any(r.avg_response_time_ms < 5000 for r in self.results if "query" in r.test_name.lower()),
            "Stats Endpoint < 200ms": any(r.avg_response_time_ms < 200 for r in self.results if "stats" in r.test_name.lower()),
            "Error Rate < 5%": overall_error_rate < 5,
            "P95 < 2s": all(r.p95_response_time_ms < 2000 for r in self.results),
            "Sustained Performance": any(r.requests_per_second > 10 for r in self.results if "sustained" in r.test_name.lower())
        }
        
        for criterion, met in criteria.items():
            status = "✅" if met else "❌"
            print(f"   {status} {criterion}")
        
        overall_success = all(criteria.values()) and overall_error_rate < 5
        
        print(f"\n🎉 Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
        
        # Save results
        report = {
            "timestamp": time.time(),
            "total_duration_ms": total_duration,
            "total_requests": total_requests,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "overall_error_rate": overall_error_rate,
            "overall_success": overall_success,
            "criteria_met": criteria,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "total_requests": r.total_requests,
                    "successful_requests": r.successful_requests,
                    "failed_requests": r.failed_requests,
                    "avg_response_time_ms": r.avg_response_time_ms,
                    "p95_response_time_ms": r.p95_response_time_ms,
                    "p99_response_time_ms": r.p99_response_time_ms,
                    "max_response_time_ms": r.max_response_time_ms,
                    "min_response_time_ms": r.min_response_time_ms,
                    "requests_per_second": r.requests_per_second,
                    "error_rate": r.error_rate,
                    "errors": r.errors
                }
                for r in self.results
            ]
        }
        
        with open("load_test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Results saved to load_test_results.json")
        
        return report

async def main():
    """Main load test function"""
    tester = LoadTester()
    report = await tester.run_all_load_tests()
    
    # Exit with appropriate code
    exit(0 if report["overall_success"] else 1)

if __name__ == "__main__":
    asyncio.run(main())
