#!/usr/bin/env python3
"""
Create Supabase Storage Bucket for L3 Cache
This script will guide you through creating the required bucket
"""

import os
import sys
import requests
import json

def create_supabase_bucket():
    """Create the ragflow-cache bucket in Supabase Storage"""
    print("🗄️ Creating Supabase Storage Bucket for L3 Cache")
    print("=" * 60)
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        print("   Please set SUPABASE_URL and SUPABASE_KEY environment variables")
        return False
    
    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ Supabase Key: {supabase_key[:20]}...")
    
    # Extract project reference from URL
    project_ref = supabase_url.split("//")[1].split(".")[0]
    print(f"✅ Project Reference: {project_ref}")
    
    # Create bucket using Supabase REST API
    bucket_name = "ragflow-cache"
    bucket_url = f"{supabase_url}/storage/v1/bucket"
    
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "apikey": supabase_key
    }
    
    bucket_data = {
        "id": bucket_name,
        "name": bucket_name,
        "public": True,
        "file_size_limit": 52428800,  # 50MB
        "allowed_mime_types": ["application/json", "text/plain", "application/octet-stream"]
    }
    
    print(f"🔄 Creating bucket '{bucket_name}'...")
    
    try:
        response = requests.post(bucket_url, headers=headers, json=bucket_data)
        
        if response.status_code == 200:
            print("✅ Bucket created successfully!")
            return True
        elif response.status_code == 409:
            print("✅ Bucket already exists!")
            return True
        else:
            print(f"❌ Failed to create bucket: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False

def test_bucket_access():
    """Test access to the created bucket"""
    print("\n🧪 Testing Bucket Access...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    bucket_name = "ragflow-cache"
    
    # Test file upload
    test_file_url = f"{supabase_url}/storage/v1/object/{bucket_name}/test-file.json"
    
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "apikey": supabase_key
    }
    
    test_data = {"test": "data", "timestamp": "2024-01-01T00:00:00Z"}
    
    try:
        response = requests.post(test_file_url, headers=headers, json=test_data)
        
        if response.status_code == 200:
            print("✅ Bucket access test successful!")
            
            # Clean up test file
            delete_url = f"{supabase_url}/storage/v1/object/{bucket_name}/test-file.json"
            requests.delete(delete_url, headers=headers)
            print("✅ Test file cleaned up")
            return True
        else:
            print(f"❌ Bucket access test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bucket access: {e}")
        return False

def print_manual_instructions():
    """Print manual setup instructions"""
    print("\n" + "=" * 60)
    print("📋 MANUAL SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1️⃣ Go to Supabase Dashboard:")
    print("   https://supabase.com/dashboard")
    
    print("\n2️⃣ Navigate to your project:")
    print("   https://supabase.com/dashboard/project/joszwyxywxdiwscmsyud")
    
    print("\n3️⃣ Go to Storage (left sidebar)")
    
    print("\n4️⃣ Click 'New bucket'")
    
    print("\n5️⃣ Configure the bucket:")
    print("   • Name: ragflow-cache")
    print("   • Public: Yes")
    print("   • File size limit: 50MB")
    print("   • Allowed MIME types: application/json, text/plain")
    
    print("\n6️⃣ Click 'Create bucket'")
    
    print("\n7️⃣ Verify the bucket appears in the list")

def main():
    """Main function"""
    print("🚀 Supabase Storage Bucket Setup for L3 Cache")
    print("=" * 60)
    
    # Try to create bucket programmatically
    success = create_supabase_bucket()
    
    if success:
        # Test bucket access
        if test_bucket_access():
            print("\n🎉 L3 Cache bucket setup complete!")
            print("✅ Bucket created and accessible")
            print("✅ L3 Cache should now work")
        else:
            print("\n⚠️ Bucket created but access test failed")
            print("   Check bucket permissions in Supabase Dashboard")
    else:
        print("\n📋 Manual setup required")
        print_manual_instructions()
    
    print("\n🎯 Next Steps:")
    print("1. Verify bucket exists in Supabase Dashboard")
    print("2. Run cache test: python test_cache_levels.py")
    print("3. Test L1/L2/L3 cache flow")

if __name__ == "__main__":
    main()
