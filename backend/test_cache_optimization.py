#!/usr/bin/env python3
"""
Cache Optimization Test - Achieve 80%+ Hit Rate
Tests realistic query patterns and cache warming strategies
"""

import os
import sys
import time
import asyncio
import json
import random
from typing import List, Dict

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from managers.cache_manager import get_cache_manager

class CacheOptimizationTest:
    """Test cache optimization strategies for 80%+ hit rate"""
    
    def __init__(self):
        self.cache = get_cache_manager()
        self.test_results = {}
    
    def generate_realistic_queries(self) -> List[str]:
        """Generate realistic query patterns (80% repeated, 20% new)"""
        base_queries = [
            "What are the legal terms and conditions?",
            "How does the API work?",
            "What is the budget for this project?",
            "What are the employee benefits?",
            "What are the technical specifications?",
            "What are the financial requirements?",
            "What are the HR policies?",
            "What are the compliance requirements?",
            "What are the security measures?",
            "What are the performance metrics?"
        ]
        
        # Generate 100 queries with 80% repetition
        queries = []
        for _ in range(100):
            if random.random() < 0.8:  # 80% repeated queries
                queries.append(random.choice(base_queries))
            else:  # 20% new queries
                queries.append(f"New query about {random.choice(['legal', 'technical', 'financial', 'hr'])} {random.randint(1, 1000)}")
        
        return queries
    
    async def test_cache_warming(self) -> Dict:
        """Test cache warming strategy"""
        print("🔥 Testing Cache Warming Strategy...")
        
        # Warm up cache with common queries
        warmup_queries = [
            "What are the legal terms?",
            "How does the API work?", 
            "What is the budget?",
            "What are the benefits?",
            "What are the specifications?"
        ]
        
        for query in warmup_queries:
            key = f"warmup:{hash(query)}"
            await self.cache.set(key, {"query": query, "answer": f"Answer for: {query}"})
        
        print(f"   ✅ Cache warmed up with {len(warmup_queries)} common queries")
        return {"warmed_queries": len(warmup_queries)}
    
    async def test_realistic_query_patterns(self) -> Dict:
        """Test realistic query patterns for 80%+ hit rate"""
        print("📊 Testing Realistic Query Patterns...")
        
        queries = self.generate_realistic_queries()
        results = {
            "total_queries": len(queries),
            "cache_hits": 0,
            "cache_misses": 0,
            "response_times": [],
            "hit_rate": 0
        }
        
        for i, query in enumerate(queries):
            key = f"query:{hash(query)}"
            start_time = time.time()
            
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["response_times"].append(response_time)
            
            if cache_level != "MISS":
                results["cache_hits"] += 1
            else:
                results["cache_misses"] += 1
                # Store the result for future hits
                await self.cache.set(key, {
                    "query": query,
                    "answer": f"Answer for: {query}",
                    "timestamp": time.time()
                })
            
            # Progress indicator
            if (i + 1) % 20 == 0:
                current_hit_rate = (results["cache_hits"] / (i + 1)) * 100
                print(f"   Progress: {i + 1}/{len(queries)} queries, Hit Rate: {current_hit_rate:.1f}%")
        
        results["hit_rate"] = (results["cache_hits"] / results["total_queries"]) * 100
        return results
    
    async def test_cache_ttl_optimization(self) -> Dict:
        """Test cache TTL optimization"""
        print("⏰ Testing Cache TTL Optimization...")
        
        # Test different TTL values
        ttl_tests = [
            {"ttl": 300, "name": "5 minutes"},
            {"ttl": 1800, "name": "30 minutes"},
            {"ttl": 3600, "name": "1 hour"},
            {"ttl": 86400, "name": "24 hours"}
        ]
        
        results = {}
        
        for ttl_test in ttl_tests:
            ttl = ttl_test["ttl"]
            name = ttl_test["name"]
            
            # Set test data with specific TTL
            test_key = f"ttl_test_{ttl}"
            await self.cache.set(test_key, {"data": f"TTL test for {name}"}, ttl=ttl)
            
            # Test immediate retrieval
            start_time = time.time()
            value, cache_level = await self.cache.get(test_key)
            response_time = (time.time() - start_time) * 1000
            
            results[name] = {
                "ttl": ttl,
                "cache_level": cache_level,
                "response_time": response_time,
                "success": value is not None
            }
        
        return results
    
    async def test_cache_size_optimization(self) -> Dict:
        """Test cache size optimization"""
        print("📏 Testing Cache Size Optimization...")
        
        # Test different cache sizes
        size_tests = [1000, 5000, 10000, 20000]
        results = {}
        
        for size in size_tests:
            # Create a new cache manager with specific size
            from managers.cache_manager import MultiLevelCache
            test_cache = MultiLevelCache(l1_size=size)
            
            # Fill cache to capacity
            for i in range(size + 100):  # Overfill to test eviction
                key = f"size_test_{i}"
                await test_cache.set(key, {"data": f"Test data {i}"})
            
            # Test hit rate after filling
            hits = 0
            misses = 0
            
            for i in range(100):  # Test first 100 items
                key = f"size_test_{i}"
                value, cache_level = await test_cache.get(key)
                
                if cache_level != "MISS":
                    hits += 1
                else:
                    misses += 1
            
            hit_rate = (hits / 100) * 100
            results[f"size_{size}"] = {
                "size": size,
                "hits": hits,
                "misses": misses,
                "hit_rate": hit_rate
            }
        
        return results
    
    async def run_optimization_test(self) -> Dict:
        """Run comprehensive cache optimization test"""
        print("🚀 Cache Optimization Test - Target: 80%+ Hit Rate")
        print("=" * 60)
        
        # Run all optimization tests
        tests = [
            ("Cache Warming", self.test_cache_warming()),
            ("Realistic Query Patterns", self.test_realistic_query_patterns()),
            ("TTL Optimization", self.test_cache_ttl_optimization()),
            ("Size Optimization", self.test_cache_size_optimization())
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
        results["final_cache_stats"] = cache_stats
        
        return results
    
    def print_optimization_results(self, results: Dict):
        """Print optimization test results"""
        print("\n" + "=" * 60)
        print("📊 CACHE OPTIMIZATION RESULTS")
        print("=" * 60)
        
        # Realistic Query Patterns Results
        if "Realistic Query Patterns" in results:
            realistic = results["Realistic Query Patterns"]
            print(f"\n📊 Realistic Query Patterns:")
            print(f"   Total Queries: {realistic['total_queries']}")
            print(f"   Cache Hits: {realistic['cache_hits']}")
            print(f"   Cache Misses: {realistic['cache_misses']}")
            print(f"   Hit Rate: {realistic['hit_rate']:.2f}%")
            
            if realistic['hit_rate'] >= 80:
                print("   ✅ Hit rate target (80%+) ACHIEVED!")
            else:
                print("   ⚠️ Hit rate below target (80%+)")
            
            if realistic['response_times']:
                avg_time = sum(realistic['response_times']) / len(realistic['response_times'])
                print(f"   Avg Response Time: {avg_time:.2f}ms")
        
        # TTL Optimization Results
        if "TTL Optimization" in results:
            ttl = results["TTL Optimization"]
            print(f"\n⏰ TTL Optimization Results:")
            for name, data in ttl.items():
                status = "✅" if data['success'] else "❌"
                print(f"   {name}: {data['cache_level']} ({data['response_time']:.2f}ms) {status}")
        
        # Size Optimization Results
        if "Size Optimization" in results:
            size = results["Size Optimization"]
            print(f"\n📏 Size Optimization Results:")
            for name, data in size.items():
                print(f"   {name}: {data['hit_rate']:.1f}% hit rate")
        
        # Final Cache Statistics
        if "final_cache_stats" in results:
            stats = results["final_cache_stats"]
            print(f"\n📊 Final Cache Statistics:")
            print(f"   Overall Hit Rate: {stats['overall']['hit_rate']:.2f}%")
            print(f"   L1 Hit Rate: {stats['l1_cache']['hit_rate']:.2f}%")
            print(f"   L2 Hit Rate: {stats['l2_cache']['hit_rate']:.2f}%")
            print(f"   L3 Hit Rate: {stats['l3_cache']['hit_rate']:.2f}%")

async def main():
    """Main optimization test function"""
    print("🚀 Starting Cache Optimization Test")
    
    try:
        # Initialize cache manager
        cache_manager = get_cache_manager()
        
        # Run optimization test
        test_suite = CacheOptimizationTest()
        results = await test_suite.run_optimization_test()
        
        # Print results
        test_suite.print_optimization_results(results)
        
        # Final assessment
        print("\n" + "=" * 60)
        print("🎯 OPTIMIZATION ASSESSMENT")
        print("=" * 60)
        
        realistic = results.get("Realistic Query Patterns", {})
        hit_rate = realistic.get("hit_rate", 0)
        
        if hit_rate >= 80:
            print("🎉 Cache optimization SUCCESSFUL!")
            print(f"✅ Hit rate target (80%+) achieved: {hit_rate:.2f}%")
        else:
            print("⚠️ Cache optimization needs improvement")
            print(f"⚠️ Current hit rate: {hit_rate:.2f}% (Target: 80%+)")
            print("\n💡 Optimization Tips:")
            print("   1. Increase cache TTL for frequently accessed data")
            print("   2. Implement cache warming for common queries")
            print("   3. Optimize cache size based on usage patterns")
            print("   4. Use query pattern analysis for better cache keys")
        
        print("\n🎉 Cache optimization test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
