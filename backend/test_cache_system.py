#!/usr/bin/env python3
"""
Multi-Level Cache System Test Suite
Tests L1, L2, L3 cache performance and hit rates
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

from managers.cache_manager import get_cache_manager, MultiLevelCache

class CachePerformanceTest:
    """Comprehensive cache performance testing"""
    
    def __init__(self):
        self.cache = get_cache_manager()
        self.test_results = {}
    
    def generate_test_data(self, count: int = 1000) -> List[Dict]:
        """Generate test data for cache testing"""
        test_data = []
        for i in range(count):
            data = {
                "id": f"test_{i}",
                "content": f"Test content {i} - " + ''.join(random.choices(string.ascii_letters, k=100)),
                "timestamp": time.time(),
                "metadata": {
                    "category": random.choice(["legal", "technical", "financial", "hr"]),
                    "priority": random.randint(1, 10),
                    "tags": [f"tag_{j}" for j in range(random.randint(1, 5))]
                }
            }
            test_data.append(data)
        return test_data
    
    async def test_cache_hit_miss(self, test_data: List[Dict]) -> Dict:
        """Test cache hit/miss patterns"""
        print("🎯 Testing Cache Hit/Miss Patterns...")
        
        results = {
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "misses": 0,
            "response_times": []
        }
        
        # First pass - all should be misses
        for i, data in enumerate(test_data[:100]):  # Test first 100 items
            key = f"test_key_{i}"
            start_time = time.time()
            
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["response_times"].append(response_time)
            
            if cache_level == "L1":
                results["l1_hits"] += 1
            elif cache_level == "L2":
                results["l2_hits"] += 1
            elif cache_level == "L3":
                results["l3_hits"] += 1
            else:
                results["misses"] += 1
        
        # Second pass - should have hits
        for i in range(50):  # Test first 50 items again
            key = f"test_key_{i}"
            start_time = time.time()
            
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["response_times"].append(response_time)
            
            if cache_level == "L1":
                results["l1_hits"] += 1
            elif cache_level == "L2":
                results["l2_hits"] += 1
            elif cache_level == "L3":
                results["l3_hits"] += 1
            else:
                results["misses"] += 1
        
        return results
    
    async def test_response_times(self, test_data: List[Dict]) -> Dict:
        """Test response times for each cache level"""
        print("⏱️ Testing Response Times...")
        
        results = {
            "l1_times": [],
            "l2_times": [],
            "l3_times": [],
            "miss_times": []
        }
        
        # Test L1 cache (should be <1ms)
        for i in range(10):
            key = f"l1_test_{i}"
            await self.cache.set(key, test_data[i])
            
            start_time = time.time()
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["l1_times"].append(response_time)
        
        # Test L2 cache (should be <10ms)
        for i in range(10):
            key = f"l2_test_{i}"
            # Clear L1 to force L2 access
            self.cache.l1_cache.delete(key)
            await self.cache.set(key, test_data[i])
            
            start_time = time.time()
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["l2_times"].append(response_time)
        
        # Test L3 cache (should be <100ms)
        for i in range(5):
            key = f"l3_test_{i}"
            # Clear L1 and L2 to force L3 access
            self.cache.l1_cache.delete(key)
            self.cache.l2_cache.delete(key)
            await self.cache.set(key, test_data[i])
            
            start_time = time.time()
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["l3_times"].append(response_time)
        
        return results
    
    async def test_hit_rate_optimization(self, test_data: List[Dict]) -> Dict:
        """Test hit rate optimization with repeated queries"""
        print("📈 Testing Hit Rate Optimization...")
        
        # Generate query patterns (80% repeated, 20% new)
        query_pattern = []
        for _ in range(200):
            if random.random() < 0.8:  # 80% repeated queries
                query_pattern.append(random.randint(0, 49))  # Repeat first 50 queries
            else:  # 20% new queries
                query_pattern.append(random.randint(50, 99))  # New queries
        
        results = {
            "total_queries": len(query_pattern),
            "cache_hits": 0,
            "cache_misses": 0,
            "response_times": []
        }
        
        for query_index in query_pattern:
            key = f"query_{query_index}"
            start_time = time.time()
            
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["response_times"].append(response_time)
            
            if cache_level != "MISS":
                results["cache_hits"] += 1
            else:
                results["cache_misses"] += 1
                # Set the value for future hits
                await self.cache.set(key, test_data[query_index % len(test_data)])
        
        return results
    
    async def test_concurrent_access(self, test_data: List[Dict]) -> Dict:
        """Test concurrent cache access"""
        print("🔄 Testing Concurrent Access...")
        
        async def concurrent_worker(worker_id: int, keys: List[str]):
            results = {"hits": 0, "misses": 0, "times": []}
            for key in keys:
                start_time = time.time()
                value, cache_level = await self.cache.get(key)
                response_time = (time.time() - start_time) * 1000
                results["times"].append(response_time)
                
                if cache_level != "MISS":
                    results["hits"] += 1
                else:
                    results["misses"] += 1
                    await self.cache.set(key, test_data[random.randint(0, len(test_data)-1)])
            
            return results
        
        # Create concurrent workers
        workers = []
        keys_per_worker = 20
        
        for i in range(5):  # 5 concurrent workers
            worker_keys = [f"concurrent_{i}_{j}" for j in range(keys_per_worker)]
            workers.append(concurrent_worker(i, worker_keys))
        
        # Run concurrent workers
        worker_results = await asyncio.gather(*workers)
        
        # Aggregate results
        total_hits = sum(r["hits"] for r in worker_results)
        total_misses = sum(r["misses"] for r in worker_results)
        all_times = []
        for r in worker_results:
            all_times.extend(r["times"])
        
        return {
            "workers": len(workers),
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate": (total_hits / (total_hits + total_misses) * 100) if (total_hits + total_misses) > 0 else 0,
            "avg_response_time": sum(all_times) / len(all_times) if all_times else 0,
            "max_response_time": max(all_times) if all_times else 0,
            "min_response_time": min(all_times) if all_times else 0
        }
    
    async def test_cache_eviction(self) -> Dict:
        """Test cache eviction policies"""
        print("🗑️ Testing Cache Eviction...")
        
        # Fill L1 cache beyond capacity
        l1_capacity = self.cache.l1_cache.max_size
        test_items = l1_capacity + 100
        
        # Add items to cache
        for i in range(test_items):
            key = f"eviction_test_{i}"
            await self.cache.set(key, f"value_{i}")
        
        # Check if old items were evicted
        old_item_exists = await self.cache.get("eviction_test_0")
        new_item_exists = await self.cache.get(f"eviction_test_{test_items-1}")
        
        return {
            "l1_capacity": l1_capacity,
            "items_added": test_items,
            "old_item_evicted": old_item_exists[0] is None,
            "new_item_present": new_item_exists[0] is not None,
            "l1_current_size": len(self.cache.l1_cache.cache)
        }
    
    async def run_comprehensive_test(self) -> Dict:
        """Run comprehensive cache system test"""
        print("🧪 Multi-Level Cache System - Comprehensive Test")
        print("=" * 60)
        
        # Generate test data
        test_data = self.generate_test_data(1000)
        
        # Run all tests
        tests = [
            ("Cache Hit/Miss", self.test_cache_hit_miss(test_data)),
            ("Response Times", self.test_response_times(test_data)),
            ("Hit Rate Optimization", self.test_hit_rate_optimization(test_data)),
            ("Concurrent Access", self.test_concurrent_access(test_data)),
            ("Cache Eviction", self.test_cache_eviction())
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
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        # Cache Hit/Miss Results
        if "Cache Hit/Miss" in results:
            hit_miss = results["Cache Hit/Miss"]
            print(f"\n🎯 Cache Hit/Miss Results:")
            print(f"   L1 Hits: {hit_miss['l1_hits']}")
            print(f"   L2 Hits: {hit_miss['l2_hits']}")
            print(f"   L3 Hits: {hit_miss['l3_hits']}")
            print(f"   Misses: {hit_miss['misses']}")
            
            avg_response_time = sum(hit_miss['response_times']) / len(hit_miss['response_times'])
            print(f"   Avg Response Time: {avg_response_time:.2f}ms")
        
        # Response Time Results
        if "Response Times" in results:
            response_times = results["Response Times"]
            print(f"\n⏱️ Response Time Results:")
            
            if response_times['l1_times']:
                l1_avg = sum(response_times['l1_times']) / len(response_times['l1_times'])
                print(f"   L1 Cache Avg: {l1_avg:.2f}ms (Target: <1ms)")
            
            if response_times['l2_times']:
                l2_avg = sum(response_times['l2_times']) / len(response_times['l2_times'])
                print(f"   L2 Cache Avg: {l2_avg:.2f}ms (Target: <10ms)")
            
            if response_times['l3_times']:
                l3_avg = sum(response_times['l3_times']) / len(response_times['l3_times'])
                print(f"   L3 Cache Avg: {l3_avg:.2f}ms (Target: <100ms)")
        
        # Hit Rate Results
        if "Hit Rate Optimization" in results:
            hit_rate = results["Hit Rate Optimization"]
            print(f"\n📈 Hit Rate Results:")
            print(f"   Total Queries: {hit_rate['total_queries']}")
            print(f"   Cache Hits: {hit_rate['cache_hits']}")
            print(f"   Cache Misses: {hit_rate['cache_misses']}")
            
            if hit_rate['total_queries'] > 0:
                hit_rate_percent = (hit_rate['cache_hits'] / hit_rate['total_queries']) * 100
                print(f"   Hit Rate: {hit_rate_percent:.2f}% (Target: >80%)")
                
                if hit_rate_percent >= 80:
                    print("   ✅ Hit rate target achieved!")
                else:
                    print("   ⚠️ Hit rate below target")
        
        # Concurrent Access Results
        if "Concurrent Access" in results:
            concurrent = results["Concurrent Access"]
            print(f"\n🔄 Concurrent Access Results:")
            print(f"   Workers: {concurrent['workers']}")
            print(f"   Total Hits: {concurrent['total_hits']}")
            print(f"   Total Misses: {concurrent['total_misses']}")
            print(f"   Hit Rate: {concurrent['hit_rate']:.2f}%")
            print(f"   Avg Response Time: {concurrent['avg_response_time']:.2f}ms")
            print(f"   Max Response Time: {concurrent['max_response_time']:.2f}ms")
        
        # Cache Eviction Results
        if "Cache Eviction" in results:
            eviction = results["Cache Eviction"]
            print(f"\n🗑️ Cache Eviction Results:")
            print(f"   L1 Capacity: {eviction['l1_capacity']}")
            print(f"   Items Added: {eviction['items_added']}")
            print(f"   Old Item Evicted: {eviction['old_item_evicted']}")
            print(f"   New Item Present: {eviction['new_item_present']}")
            print(f"   Current L1 Size: {eviction['l1_current_size']}")
        
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
            
            print(f"\n   L3 Cache:")
            print(f"     Connected: {stats['l3_cache']['connected']}")
            if stats['l3_cache']['connected']:
                print(f"     Hit Rate: {stats['l3_cache']['hit_rate']:.2f}%")

async def main():
    """Main test function"""
    print("🚀 Starting Multi-Level Cache System Test")
    
    try:
        # Initialize cache manager
        cache_manager = get_cache_manager()
        
        # Run comprehensive test
        test_suite = CachePerformanceTest()
        results = await test_suite.run_comprehensive_test()
        
        # Print results
        test_suite.print_results(results)
        
        # Final assessment
        print("\n" + "=" * 60)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 60)
        
        overall_hit_rate = results.get("cache_statistics", {}).get("overall", {}).get("hit_rate", 0)
        
        if overall_hit_rate >= 80:
            print("✅ Multi-level cache system is performing optimally!")
            print("✅ Hit rate target (80%+) achieved")
        else:
            print("⚠️ Multi-level cache system needs optimization")
            print(f"⚠️ Hit rate ({overall_hit_rate:.2f}%) below target (80%+)")
        
        print("\n🎉 Multi-level cache system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
