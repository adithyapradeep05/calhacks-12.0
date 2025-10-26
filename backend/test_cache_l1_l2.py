#!/usr/bin/env python3
"""
L1/L2 Cache System Test (L3 Supabase Storage requires bucket setup)
Tests L1 (In-memory LRU) and L2 (Redis) cache performance
"""

import os
import sys
import time
import asyncio
import json
import random
import string
from typing import List, Dict

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from managers.cache_manager import get_cache_manager

class L1L2CacheTest:
    """Test L1 and L2 cache performance"""
    
    def __init__(self):
        self.cache = get_cache_manager()
        self.test_results = {}
    
    def generate_test_data(self, count: int = 100) -> List[Dict]:
        """Generate test data for cache testing"""
        test_data = []
        for i in range(count):
            data = {
                "id": f"test_{i}",
                "content": f"Test content {i} - " + ''.join(random.choices(string.ascii_letters, k=50)),
                "timestamp": time.time(),
                "metadata": {
                    "category": random.choice(["legal", "technical", "financial", "hr"]),
                    "priority": random.randint(1, 10)
                }
            }
            test_data.append(data)
        return test_data
    
    async def test_l1_cache_performance(self, test_data: List[Dict]) -> Dict:
        """Test L1 cache (in-memory LRU) performance"""
        print("🚀 Testing L1 Cache (In-memory LRU) Performance...")
        
        results = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l1_response_times": [],
            "l1_hit_rate": 0
        }
        
        # Test L1 cache directly
        for i, data in enumerate(test_data[:50]):  # Test first 50 items
            key = f"l1_test_{i}"
            
            # First access (should be miss)
            start_time = time.time()
            value = self.cache.l1_cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["l1_response_times"].append(response_time)
            
            if value is None:
                results["l1_misses"] += 1
                # Set the value
                self.cache.l1_cache.set(key, data)
            else:
                results["l1_hits"] += 1
        
        # Second access (should be hits)
        for i in range(25):  # Test first 25 items again
            key = f"l1_test_{i}"
            start_time = time.time()
            value = self.cache.l1_cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["l1_response_times"].append(response_time)
            
            if value is not None:
                results["l1_hits"] += 1
            else:
                results["l1_misses"] += 1
        
        # Calculate hit rate
        total_requests = results["l1_hits"] + results["l1_misses"]
        results["l1_hit_rate"] = (results["l1_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return results
    
    async def test_l2_cache_performance(self, test_data: List[Dict]) -> Dict:
        """Test L2 cache (Redis) performance"""
        print("🔴 Testing L2 Cache (Redis) Performance...")
        
        results = {
            "l2_hits": 0,
            "l2_misses": 0,
            "l2_response_times": [],
            "l2_hit_rate": 0
        }
        
        # Test L2 cache directly
        for i, data in enumerate(test_data[:30]):  # Test first 30 items
            key = f"l2_test_{i}"
            
            # First access (should be miss)
            start_time = time.time()
            value = self.cache.l2_cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["l2_response_times"].append(response_time)
            
            if value is None:
                results["l2_misses"] += 1
                # Set the value
                self.cache.l2_cache.set(key, data)
            else:
                results["l2_hits"] += 1
        
        # Second access (should be hits)
        for i in range(15):  # Test first 15 items again
            key = f"l2_test_{i}"
            start_time = time.time()
            value = self.cache.l2_cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["l2_response_times"].append(response_time)
            
            if value is not None:
                results["l2_hits"] += 1
            else:
                results["l2_misses"] += 1
        
        # Calculate hit rate
        total_requests = results["l2_hits"] + results["l2_misses"]
        results["l2_hit_rate"] = (results["l2_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return results
    
    async def test_multi_level_cache_flow(self, test_data: List[Dict]) -> Dict:
        """Test multi-level cache flow (L1 -> L2 -> MISS)"""
        print("🔄 Testing Multi-Level Cache Flow...")
        
        results = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "response_times": [],
            "cache_levels": []
        }
        
        # Test multi-level cache
        for i, data in enumerate(test_data[:20]):  # Test first 20 items
            key = f"multi_test_{i}"
            
            start_time = time.time()
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            
            results["response_times"].append(response_time)
            results["cache_levels"].append(cache_level)
            
            if cache_level == "L1":
                results["l1_hits"] += 1
            elif cache_level == "L2":
                results["l2_hits"] += 1
            else:
                results["misses"] += 1
                # Set the value for future hits
                await self.cache.set(key, data)
        
        # Test repeated access (should hit L1)
        for i in range(10):  # Test first 10 items again
            key = f"multi_test_{i}"
            
            start_time = time.time()
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            
            results["response_times"].append(response_time)
            results["cache_levels"].append(cache_level)
            
            if cache_level == "L1":
                results["l1_hits"] += 1
            elif cache_level == "L2":
                results["l2_hits"] += 1
            else:
                results["misses"] += 1
        
        return results
    
    async def test_response_time_targets(self) -> Dict:
        """Test if response times meet targets"""
        print("⏱️ Testing Response Time Targets...")
        
        results = {
            "l1_target_met": False,
            "l2_target_met": False,
            "l1_avg_time": 0,
            "l2_avg_time": 0,
            "l1_max_time": 0,
            "l2_max_time": 0
        }
        
        # Test L1 response times (target: <1ms)
        l1_times = []
        for i in range(10):
            key = f"perf_l1_{i}"
            self.cache.l1_cache.set(key, f"test_data_{i}")
            
            start_time = time.time()
            value = self.cache.l1_cache.get(key)
            response_time = (time.time() - start_time) * 1000
            l1_times.append(response_time)
        
        results["l1_avg_time"] = sum(l1_times) / len(l1_times)
        results["l1_max_time"] = max(l1_times)
        results["l1_target_met"] = results["l1_avg_time"] < 1.0
        
        # Test L2 response times (target: <10ms)
        l2_times = []
        for i in range(10):
            key = f"perf_l2_{i}"
            self.cache.l2_cache.set(key, f"test_data_{i}")
            
            # Clear L1 to force L2 access
            self.cache.l1_cache.delete(key)
            
            start_time = time.time()
            value = self.cache.l2_cache.get(key)
            response_time = (time.time() - start_time) * 1000
            l2_times.append(response_time)
        
        results["l2_avg_time"] = sum(l2_times) / len(l2_times)
        results["l2_max_time"] = max(l2_times)
        results["l2_target_met"] = results["l2_avg_time"] < 10.0
        
        return results
    
    async def run_comprehensive_test(self) -> Dict:
        """Run comprehensive L1/L2 cache test"""
        print("🧪 L1/L2 Cache System - Comprehensive Test")
        print("=" * 60)
        
        # Generate test data
        test_data = self.generate_test_data(100)
        
        # Run all tests
        tests = [
            ("L1 Cache Performance", self.test_l1_cache_performance(test_data)),
            ("L2 Cache Performance", self.test_l2_cache_performance(test_data)),
            ("Multi-Level Cache Flow", self.test_multi_level_cache_flow(test_data)),
            ("Response Time Targets", self.test_response_time_targets())
        ]
        
        results = {}
        
        for test_name, test_coro in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                result = await test_coro
                results[test_name] = result
                print(f"   ✅ {test_name} completed")
            except Exception as e:
                print(f"   ❌ {test_name} failed: {e}")
                results[test_name] = {"error": str(e)}
        
        # Get final cache statistics
        cache_stats = self.cache.get_stats()
        results["cache_statistics"] = cache_stats
        
        return results
    
    def print_results(self, results: Dict):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 L1/L2 CACHE TEST RESULTS")
        print("=" * 60)
        
        # L1 Cache Results
        if "L1 Cache Performance" in results:
            l1 = results["L1 Cache Performance"]
            print(f"\n🚀 L1 Cache (In-memory LRU) Results:")
            print(f"   Hits: {l1['l1_hits']}")
            print(f"   Misses: {l1['l1_misses']}")
            print(f"   Hit Rate: {l1['l1_hit_rate']:.2f}%")
            if l1['l1_response_times']:
                avg_time = sum(l1['l1_response_times']) / len(l1['l1_response_times'])
                print(f"   Avg Response Time: {avg_time:.2f}ms")
        
        # L2 Cache Results
        if "L2 Cache Performance" in results:
            l2 = results["L2 Cache Performance"]
            print(f"\n🔴 L2 Cache (Redis) Results:")
            print(f"   Hits: {l2['l2_hits']}")
            print(f"   Misses: {l2['l2_misses']}")
            print(f"   Hit Rate: {l2['l2_hit_rate']:.2f}%")
            if l2['l2_response_times']:
                avg_time = sum(l2['l2_response_times']) / len(l2['l2_response_times'])
                print(f"   Avg Response Time: {avg_time:.2f}ms")
        
        # Multi-Level Cache Results
        if "Multi-Level Cache Flow" in results:
            multi = results["Multi-Level Cache Flow"]
            print(f"\n🔄 Multi-Level Cache Flow Results:")
            print(f"   L1 Hits: {multi['l1_hits']}")
            print(f"   L2 Hits: {multi['l2_hits']}")
            print(f"   Misses: {multi['misses']}")
            if multi['response_times']:
                avg_time = sum(multi['response_times']) / len(multi['response_times'])
                print(f"   Avg Response Time: {avg_time:.2f}ms")
        
        # Response Time Targets
        if "Response Time Targets" in results:
            perf = results["Response Time Targets"]
            print(f"\n⏱️ Response Time Targets:")
            print(f"   L1 Avg Time: {perf['l1_avg_time']:.2f}ms (Target: <1ms) {'✅' if perf['l1_target_met'] else '❌'}")
            print(f"   L1 Max Time: {perf['l1_max_time']:.2f}ms")
            print(f"   L2 Avg Time: {perf['l2_avg_time']:.2f}ms (Target: <10ms) {'✅' if perf['l2_target_met'] else '❌'}")
            print(f"   L2 Max Time: {perf['l2_max_time']:.2f}ms")
        
        # Overall Cache Statistics
        if "cache_statistics" in results:
            stats = results["cache_statistics"]
            print(f"\n📊 Overall Cache Statistics:")
            print(f"   Total Requests: {stats['overall']['total_requests']}")
            print(f"   Cache Hits: {stats['overall']['cache_hits']}")
            print(f"   Cache Misses: {stats['overall']['cache_misses']}")
            print(f"   Overall Hit Rate: {stats['overall']['hit_rate']:.2f}%")
            
            print(f"\n   L1 Cache:")
            print(f"     Size: {stats['l1_cache']['size']}/{stats['l1_cache']['max_size']}")
            print(f"     Hit Rate: {stats['l1_cache']['hit_rate']:.2f}%")
            
            print(f"\n   L2 Cache:")
            print(f"     Connected: {stats['l2_cache']['connected']}")
            if stats['l2_cache']['connected']:
                print(f"     Hit Rate: {stats['l2_cache']['hit_rate']:.2f}%")

async def main():
    """Main test function"""
    print("🚀 Starting L1/L2 Cache System Test")
    
    try:
        # Initialize cache manager
        cache_manager = get_cache_manager()
        
        # Run comprehensive test
        test_suite = L1L2CacheTest()
        results = await test_suite.run_comprehensive_test()
        
        # Print results
        test_suite.print_results(results)
        
        # Final assessment
        print("\n" + "=" * 60)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 60)
        
        # Check L1 performance
        l1_perf = results.get("L1 Cache Performance", {})
        l1_hit_rate = l1_perf.get("l1_hit_rate", 0)
        
        # Check L2 performance
        l2_perf = results.get("L2 Cache Performance", {})
        l2_hit_rate = l2_perf.get("l2_hit_rate", 0)
        
        # Check response time targets
        perf_targets = results.get("Response Time Targets", {})
        l1_target_met = perf_targets.get("l1_target_met", False)
        l2_target_met = perf_targets.get("l2_target_met", False)
        
        print(f"L1 Cache Hit Rate: {l1_hit_rate:.2f}%")
        print(f"L2 Cache Hit Rate: {l2_hit_rate:.2f}%")
        print(f"L1 Response Time Target: {'✅ MET' if l1_target_met else '❌ NOT MET'}")
        print(f"L2 Response Time Target: {'✅ MET' if l2_target_met else '❌ NOT MET'}")
        
        if l1_hit_rate >= 80 and l2_hit_rate >= 60 and l1_target_met and l2_target_met:
            print("\n🎉 L1/L2 Cache system is performing optimally!")
            print("✅ Hit rate targets achieved")
            print("✅ Response time targets achieved")
        else:
            print("\n⚠️ L1/L2 Cache system needs optimization")
            if l1_hit_rate < 80:
                print(f"⚠️ L1 hit rate ({l1_hit_rate:.2f}%) below target (80%+)")
            if l2_hit_rate < 60:
                print(f"⚠️ L2 hit rate ({l2_hit_rate:.2f}%) below target (60%+)")
            if not l1_target_met:
                print("⚠️ L1 response time target not met")
            if not l2_target_met:
                print("⚠️ L2 response time target not met")
        
        print("\n🎉 L1/L2 cache system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
