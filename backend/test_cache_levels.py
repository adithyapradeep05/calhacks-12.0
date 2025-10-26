#!/usr/bin/env python3
"""
Test All Cache Levels (L1/L2/L3) - Comprehensive Cache Testing
Ensures L1, L2, and L3 caches work independently and together
"""

import os
import sys
import time
import asyncio
import json
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from managers.cache_manager import get_cache_manager

class CacheLevelTester:
    """Test all cache levels independently and together"""
    
    def __init__(self):
        self.cache = get_cache_manager()
        self.test_results = {}
    
    async def test_l1_cache_only(self) -> Dict[str, Any]:
        """Test L1 cache (in-memory) independently"""
        print("🚀 Testing L1 Cache (In-Memory LRU)...")
        
        # Clear L2 and L3 to test L1 only
        if self.cache.l2_cache.connected:
            self.cache.l2_cache.clear()
        if self.cache.l3_cache.connected:
            try:
                # Clear L3 cache files
                files = self.cache.l3_cache.list_files()
                for file in files:
                    self.cache.l3_cache.delete(file['name'])
            except:
                pass
        
        results = {
            "total_operations": 0,
            "hits": 0,
            "misses": 0,
            "response_times": [],
            "success": True
        }
        
        # Test L1 cache operations
        test_data = {"test": "l1_data", "timestamp": time.time()}
        
        for i in range(50):
            key = f"l1_test_{i}"
            start_time = time.time()
            
            # Set operation
            await self.cache.set(key, test_data)
            results["total_operations"] += 1
            
            # Get operation
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["response_times"].append(response_time)
            
            if cache_level == "L1":
                results["hits"] += 1
            else:
                results["misses"] += 1
        
        results["hit_rate"] = (results["hits"] / results["total_operations"]) * 100
        results["avg_response_time"] = sum(results["response_times"]) / len(results["response_times"])
        
        print(f"   ✅ L1 Cache Test Results:")
        print(f"   📊 Operations: {results['total_operations']}")
        print(f"   🎯 Hits: {results['hits']}")
        print(f"   ❌ Misses: {results['misses']}")
        print(f"   📈 Hit Rate: {results['hit_rate']:.2f}%")
        print(f"   ⏱️ Avg Response Time: {results['avg_response_time']:.2f}ms")
        
        return results
    
    async def test_l2_cache_only(self) -> Dict[str, Any]:
        """Test L2 cache (Redis) independently"""
        print("\n🔴 Testing L2 Cache (Redis)...")
        
        if not self.cache.l2_cache.connected:
            print("   ❌ Redis client not available")
            return {"success": False, "error": "Redis not connected"}
        
        # Clear L1 cache to force L2 access
        self.cache.l1_cache.clear()
        
        results = {
            "total_operations": 0,
            "hits": 0,
            "misses": 0,
            "response_times": [],
            "success": True
        }
        
        # Test L2 cache operations
        test_data = {"test": "l2_data", "timestamp": time.time()}
        
        for i in range(50):
            key = f"l2_test_{i}"
            start_time = time.time()
            
            # Set operation (bypass L1)
            self.cache.l2_cache.set(key, test_data)
            results["total_operations"] += 1
            
            # Get operation
            value, cache_level = await self.cache.get(key)
            response_time = (time.time() - start_time) * 1000
            results["response_times"].append(response_time)
            
            if cache_level == "L2":
                results["hits"] += 1
            else:
                results["misses"] += 1
        
        results["hit_rate"] = (results["hits"] / results["total_operations"]) * 100
        results["avg_response_time"] = sum(results["response_times"]) / len(results["response_times"])
        
        print(f"   ✅ L2 Cache Test Results:")
        print(f"   📊 Operations: {results['total_operations']}")
        print(f"   🎯 Hits: {results['hits']}")
        print(f"   ❌ Misses: {results['misses']}")
        print(f"   📈 Hit Rate: {results['hit_rate']:.2f}%")
        print(f"   ⏱️ Avg Response Time: {results['avg_response_time']:.2f}ms")
        
        return results
    
    async def test_l3_cache_only(self) -> Dict[str, Any]:
        """Test L3 cache (Supabase Storage) independently"""
        print("\n🔵 Testing L3 Cache (Supabase Storage)...")
        
        if not self.cache.l3_cache.connected:
            print("   ❌ Supabase Storage client not available")
            return {"success": False, "error": "Supabase Storage not connected"}
        
        # Clear L1 and L2 to force L3 access
        self.cache.l1_cache.clear()
        if self.cache.l2_cache.connected:
            self.cache.l2_cache.clear()
        
        results = {
            "total_operations": 0,
            "hits": 0,
            "misses": 0,
            "response_times": [],
            "success": True
        }
        
        # Test L3 cache operations
        test_data = {"test": "l3_data", "timestamp": time.time()}
        
        for i in range(20):  # Fewer tests for L3 (slower)
            key = f"l3_test_{i}"
            start_time = time.time()
            
            # Set operation (bypass L1/L2)
            try:
                self.cache.l3_cache.set(key, test_data)
                results["total_operations"] += 1
                
                # Get operation
                value, cache_level = await self.cache.get(key)
                response_time = (time.time() - start_time) * 1000
                results["response_times"].append(response_time)
                
                if cache_level == "L3":
                    results["hits"] += 1
                else:
                    results["misses"] += 1
                    
            except Exception as e:
                print(f"   ⚠️ L3 operation {i} failed: {e}")
                results["misses"] += 1
        
        if results["total_operations"] > 0:
            results["hit_rate"] = (results["hits"] / results["total_operations"]) * 100
            results["avg_response_time"] = sum(results["response_times"]) / len(results["response_times"])
        else:
            results["hit_rate"] = 0
            results["avg_response_time"] = 0
        
        print(f"   ✅ L3 Cache Test Results:")
        print(f"   📊 Operations: {results['total_operations']}")
        print(f"   🎯 Hits: {results['hits']}")
        print(f"   ❌ Misses: {results['misses']}")
        print(f"   📈 Hit Rate: {results['hit_rate']:.2f}%")
        print(f"   ⏱️ Avg Response Time: {results['avg_response_time']:.2f}ms")
        
        return results
    
    async def test_cache_flow(self) -> Dict[str, Any]:
        """Test cache flow: L1 → L2 → L3"""
        print("\n🔄 Testing Cache Flow (L1 → L2 → L3)...")
        
        results = {
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "misses": 0,
            "response_times": [],
            "flow_tests": []
        }
        
        test_key = "flow_test_key"
        test_data = {"test": "flow_data", "timestamp": time.time()}
        
        # Test 1: Initial miss, set in all levels
        print("   🔍 Test 1: Initial miss and set")
        start_time = time.time()
        value, cache_level = await self.cache.get(test_key)
        response_time = (time.time() - start_time) * 1000
        results["flow_tests"].append({"test": "initial_miss", "level": cache_level, "time": response_time})
        
        if cache_level == "MISS":
            results["misses"] += 1
            await self.cache.set(test_key, test_data)
            print(f"   ✅ Set in all levels (L1/L2/L3)")
        
        # Test 2: L1 hit
        print("   🔍 Test 2: L1 hit")
        start_time = time.time()
        value, cache_level = await self.cache.get(test_key)
        response_time = (time.time() - start_time) * 1000
        results["flow_tests"].append({"test": "l1_hit", "level": cache_level, "time": response_time})
        
        if cache_level == "L1":
            results["l1_hits"] += 1
            print(f"   ✅ L1 hit confirmed ({response_time:.2f}ms)")
        
        # Test 3: L2 hit (clear L1)
        print("   🔍 Test 3: L2 hit (L1 cleared)")
        if test_key in self.cache.l1_cache.cache:
            del self.cache.l1_cache.cache[test_key]
        
        start_time = time.time()
        value, cache_level = await self.cache.get(test_key)
        response_time = (time.time() - start_time) * 1000
        results["flow_tests"].append({"test": "l2_hit", "level": cache_level, "time": response_time})
        
        if cache_level == "L2":
            results["l2_hits"] += 1
            print(f"   ✅ L2 hit confirmed ({response_time:.2f}ms)")
        
        # Test 4: L3 hit (clear L1 and L2)
        print("   🔍 Test 4: L3 hit (L1/L2 cleared)")
        if test_key in self.cache.l1_cache.cache:
            del self.cache.l1_cache.cache[test_key]
        if self.cache.l2_cache.connected:
            self.cache.l2_cache.delete(test_key)
        
        start_time = time.time()
        value, cache_level = await self.cache.get(test_key)
        response_time = (time.time() - start_time) * 1000
        results["flow_tests"].append({"test": "l3_hit", "level": cache_level, "time": response_time})
        
        if cache_level == "L3":
            results["l3_hits"] += 1
            print(f"   ✅ L3 hit confirmed ({response_time:.2f}ms)")
        else:
            print(f"   ⚠️ L3 hit failed, got: {cache_level}")
        
        return results
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive cache testing"""
        print("🧪 Comprehensive Cache Level Testing")
        print("=" * 60)
        
        results = {}
        
        # Test each cache level independently
        tests = [
            ("L1 Cache", self.test_l1_cache_only()),
            ("L2 Cache", self.test_l2_cache_only()),
            ("L3 Cache", self.test_l3_cache_only()),
            ("Cache Flow", self.test_cache_flow())
        ]
        
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
    
    def print_comprehensive_results(self, results: Dict):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE CACHE TEST RESULTS")
        print("=" * 60)
        
        # L1 Cache Results
        if "L1 Cache" in results and results["L1 Cache"].get("success", True):
            l1 = results["L1 Cache"]
            print(f"\n🚀 L1 Cache (In-Memory LRU):")
            print(f"   Operations: {l1['total_operations']}")
            print(f"   Hit Rate: {l1['hit_rate']:.2f}%")
            print(f"   Avg Response Time: {l1['avg_response_time']:.2f}ms")
            print(f"   Status: {'✅ WORKING' if l1['hit_rate'] > 80 else '⚠️ NEEDS IMPROVEMENT'}")
        
        # L2 Cache Results
        if "L2 Cache" in results:
            l2 = results["L2 Cache"]
            if l2.get("success", True):
                print(f"\n🔴 L2 Cache (Redis):")
                print(f"   Operations: {l2['total_operations']}")
                print(f"   Hit Rate: {l2['hit_rate']:.2f}%")
                print(f"   Avg Response Time: {l2['avg_response_time']:.2f}ms")
                print(f"   Status: {'✅ WORKING' if l2['hit_rate'] > 60 else '⚠️ NEEDS IMPROVEMENT'}")
            else:
                print(f"\n🔴 L2 Cache (Redis): ❌ NOT WORKING")
                print(f"   Error: {l2.get('error', 'Unknown error')}")
        
        # L3 Cache Results
        if "L3 Cache" in results:
            l3 = results["L3 Cache"]
            if l3.get("success", True):
                print(f"\n🔵 L3 Cache (Supabase Storage):")
                print(f"   Operations: {l3['total_operations']}")
                print(f"   Hit Rate: {l3['hit_rate']:.2f}%")
                print(f"   Avg Response Time: {l3['avg_response_time']:.2f}ms")
                print(f"   Status: {'✅ WORKING' if l3['hit_rate'] > 0 else '⚠️ NEEDS IMPROVEMENT'}")
            else:
                print(f"\n🔵 L3 Cache (Supabase Storage): ❌ NOT WORKING")
                print(f"   Error: {l3.get('error', 'Unknown error')}")
        
        # Cache Flow Results
        if "Cache Flow" in results:
            flow = results["Cache Flow"]
            print(f"\n🔄 Cache Flow (L1 → L2 → L3):")
            print(f"   L1 Hits: {flow['l1_hits']}")
            print(f"   L2 Hits: {flow['l2_hits']}")
            print(f"   L3 Hits: {flow['l3_hits']}")
            print(f"   Misses: {flow['misses']}")
            
            # Check flow tests
            for test in flow.get("flow_tests", []):
                status = "✅" if test["level"] in ["L1", "L2", "L3"] else "❌"
                print(f"   {test['test']}: {test['level']} ({test['time']:.2f}ms) {status}")
        
        # Final Assessment
        print("\n" + "=" * 60)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 60)
        
        l1_working = results.get("L1 Cache", {}).get("success", True) and results.get("L1 Cache", {}).get("hit_rate", 0) > 0
        l2_working = results.get("L2 Cache", {}).get("success", True) and results.get("L2 Cache", {}).get("hit_rate", 0) > 0
        l3_working = results.get("L3 Cache", {}).get("success", True) and results.get("L3 Cache", {}).get("hit_rate", 0) > 0
        
        print(f"L1 Cache: {'✅ WORKING' if l1_working else '❌ NOT WORKING'}")
        print(f"L2 Cache: {'✅ WORKING' if l2_working else '❌ NOT WORKING'}")
        print(f"L3 Cache: {'✅ WORKING' if l3_working else '❌ NOT WORKING'}")
        
        if l1_working and l2_working and l3_working:
            print("\n🎉 ALL CACHE LEVELS WORKING!")
            print("✅ L1/L2/L3 cache system is fully functional")
        elif l1_working and l2_working:
            print("\n⚠️ L1/L2 WORKING, L3 NEEDS FIXING")
            print("🔧 Fix L3 cache (Supabase Storage bucket)")
        elif l1_working:
            print("\n⚠️ ONLY L1 WORKING")
            print("🔧 Fix L2 cache (Redis) and L3 cache (Supabase Storage)")
        else:
            print("\n❌ CACHE SYSTEM NEEDS MAJOR FIXING")
            print("🔧 Check all cache configurations")

async def main():
    """Main testing function"""
    print("🚀 Starting Comprehensive Cache Level Testing")
    
    try:
        # Initialize cache manager
        cache_manager = get_cache_manager()
        
        # Run comprehensive test
        tester = CacheLevelTester()
        results = await tester.run_comprehensive_test()
        
        # Print results
        tester.print_comprehensive_results(results)
        
        print("\n🎉 Comprehensive cache testing completed!")
        
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
