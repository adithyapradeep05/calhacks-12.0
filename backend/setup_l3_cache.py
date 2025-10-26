#!/usr/bin/env python3
"""
L3 Cache Setup Script - Supabase Storage Bucket
Creates the required bucket for L3 cache functionality
"""

import os
import sys
import time
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

def setup_l3_cache_bucket() -> Dict[str, Any]:
    """Setup L3 cache bucket in Supabase Storage"""
    print("🗄️ Setting up L3 Cache (Supabase Storage)")
    print("=" * 50)
    
    if not SUPABASE_AVAILABLE:
        return {
            "success": False,
            "error": "Supabase client not available",
            "instructions": "Install supabase package: pip install supabase"
        }
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        return {
            "success": False,
            "error": "Supabase credentials not found",
            "instructions": "Set SUPABASE_URL and SUPABASE_KEY environment variables"
        }
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
        
        # Check if bucket already exists
        try:
            existing_buckets = supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in existing_buckets]
            
            if "ragflow-cache" in bucket_names:
                print("✅ ragflow-cache bucket already exists")
                return {
                    "success": True,
                    "message": "Bucket already exists",
                    "bucket_name": "ragflow-cache"
                }
        except Exception as e:
            print(f"⚠️ Could not list existing buckets: {e}")
        
        # Create the bucket
        print("🔄 Creating ragflow-cache bucket...")
        
        # Note: Supabase Python client doesn't have direct bucket creation
        # This needs to be done through the Supabase Dashboard or CLI
        print("📋 Manual Setup Required:")
        print("   1. Go to Supabase Dashboard: https://supabase.com/dashboard")
        print("   2. Navigate to your project: https://supabase.com/dashboard/project/joszwyxywxdiwscmsyud")
        print("   3. Go to Storage (left sidebar)")
        print("   4. Click 'New bucket'")
        print("   5. Name: 'ragflow-cache'")
        print("   6. Set as Public: Yes (for cache access)")
        print("   7. Click 'Create bucket'")
        
        return {
            "success": False,
            "error": "Manual setup required",
            "instructions": "Create bucket manually in Supabase Dashboard",
            "bucket_name": "ragflow-cache",
            "dashboard_url": "https://supabase.com/dashboard/project/joszwyxywxdiwscmsyud/storage"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Supabase connection failed: {e}",
            "instructions": "Check your Supabase credentials and network connection"
        }

def test_l3_cache_connection() -> Dict[str, Any]:
    """Test L3 cache connection after bucket creation"""
    print("\n🧪 Testing L3 Cache Connection...")
    
    if not SUPABASE_AVAILABLE:
        return {
            "success": False,
            "error": "Supabase client not available"
        }
    
    try:
        from managers.cache_manager import get_cache_manager
        cache_manager = get_cache_manager()
        
        # Test L3 cache operations
        test_key = f"l3_test_{int(time.time())}"
        test_data = {"test": "data", "timestamp": time.time()}
        
        # Test set operation
        print("🔄 Testing L3 cache set operation...")
        set_success = cache_manager.l3_cache.set(test_key, test_data, ttl=3600)
        
        if set_success:
            print("✅ L3 cache set operation successful")
        else:
            print("❌ L3 cache set operation failed")
            return {
                "success": False,
                "error": "L3 cache set operation failed",
                "instructions": "Check if ragflow-cache bucket exists in Supabase Storage"
            }
        
        # Test get operation
        print("🔄 Testing L3 cache get operation...")
        retrieved_data = cache_manager.l3_cache.get(test_key)
        
        if retrieved_data:
            print("✅ L3 cache get operation successful")
            print(f"   Retrieved data: {retrieved_data}")
        else:
            print("❌ L3 cache get operation failed")
            return {
                "success": False,
                "error": "L3 cache get operation failed",
                "instructions": "Check bucket permissions and network connection"
            }
        
        # Test delete operation
        print("🔄 Testing L3 cache delete operation...")
        delete_success = cache_manager.l3_cache.delete(test_key)
        
        if delete_success:
            print("✅ L3 cache delete operation successful")
        else:
            print("⚠️ L3 cache delete operation failed (non-critical)")
        
        return {
            "success": True,
            "message": "L3 cache connection successful",
            "operations": {
                "set": set_success,
                "get": retrieved_data is not None,
                "delete": delete_success
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"L3 cache test failed: {e}",
            "instructions": "Check cache manager configuration and Supabase connection"
        }

def print_setup_instructions():
    """Print detailed setup instructions"""
    print("\n" + "=" * 60)
    print("📋 L3 CACHE SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1️⃣ Create Supabase Storage Bucket:")
    print("   • Go to: https://supabase.com/dashboard")
    print("   • Navigate to: https://supabase.com/dashboard/project/joszwyxywxdiwscmsyud")
    print("   • Click 'Storage' in the left sidebar")
    print("   • Click 'New bucket'")
    print("   • Name: 'ragflow-cache'")
    print("   • Public: Yes (for cache access)")
    print("   • Click 'Create bucket'")
    
    print("\n2️⃣ Verify Bucket Creation:")
    print("   • Check that 'ragflow-cache' appears in the bucket list")
    print("   • Ensure it's marked as public")
    
    print("\n3️⃣ Test L3 Cache:")
    print("   • Run: python setup_l3_cache.py")
    print("   • Check for successful connection test")
    
    print("\n4️⃣ Alternative: Use Supabase CLI:")
    print("   • Install: npm install -g supabase")
    print("   • Login: supabase login")
    print("   • Link: supabase link --project-ref joszwyxywxdiwscmsyud")
    print("   • Create bucket: supabase storage create ragflow-cache --public")

def main():
    """Main setup function"""
    print("🚀 L3 Cache Setup Script")
    print("=" * 50)
    
    # Step 1: Setup bucket
    setup_result = setup_l3_cache_bucket()
    
    if setup_result["success"]:
        print("✅ L3 cache bucket setup successful")
    else:
        print(f"❌ L3 cache bucket setup failed: {setup_result['error']}")
        print(f"📋 Instructions: {setup_result.get('instructions', 'See instructions below')}")
        
        if "dashboard_url" in setup_result:
            print(f"🔗 Dashboard URL: {setup_result['dashboard_url']}")
    
    # Step 2: Test connection (if bucket exists)
    if setup_result["success"] or "bucket_name" in setup_result:
        test_result = test_l3_cache_connection()
        
        if test_result["success"]:
            print("\n🎉 L3 Cache Setup Complete!")
            print("✅ All L3 cache operations working")
        else:
            print(f"\n⚠️ L3 Cache Test Failed: {test_result['error']}")
            print(f"📋 Instructions: {test_result.get('instructions', 'Check setup')}")
    else:
        print("\n📋 Manual Setup Required")
        print_setup_instructions()
    
    print("\n🎯 Next Steps:")
    print("1. Complete L3 cache setup (if not done)")
    print("2. Run cache optimization test: python test_cache_optimization.py")
    print("3. Test full multi-level cache system")

if __name__ == "__main__":
    main()
