#!/usr/bin/env python3
"""
Supabase Schema Setup Script
Helps set up the database schema in Supabase
"""

import os
import sys

def print_instructions():
    """Print instructions for setting up Supabase schema"""
    print("🗄️ RAGFlow Supabase Schema Setup")
    print("=" * 50)
    print()
    print("The database tables need to be created in your Supabase project.")
    print("Follow these steps:")
    print()
    print("1️⃣ Go to your Supabase Dashboard:")
    print("   https://supabase.com/dashboard")
    print()
    print("2️⃣ Navigate to your project:")
    print("   https://joszwyxywxdiwscmsyud.supabase.co")
    print()
    print("3️⃣ Go to SQL Editor (left sidebar)")
    print()
    print("4️⃣ Copy and paste the following SQL schema:")
    print("   (The schema is in: backend/supabase_schema.sql)")
    print()
    print("5️⃣ Click 'Run' to execute the schema")
    print()
    print("6️⃣ Verify tables were created by checking the 'Table Editor'")
    print()
    print("📋 Required Tables:")
    print("   ✅ documents")
    print("   ✅ query_logs") 
    print("   ✅ category_stats")
    print("   ✅ embedding_metadata")
    print()
    print("🔧 Alternative: Use Supabase CLI")
    print("   If you have Supabase CLI installed:")
    print("   supabase db reset")
    print("   supabase db push")
    print()

def show_schema():
    """Display the schema content"""
    schema_file = "supabase_schema.sql"
    if os.path.exists(schema_file):
        print("📄 Schema Content:")
        print("=" * 50)
        with open(schema_file, 'r') as f:
            print(f.read())
    else:
        print("❌ Schema file not found: supabase_schema.sql")

def main():
    """Main setup function"""
    print_instructions()
    
    print("\n" + "=" * 50)
    print("📄 SCHEMA FILE LOCATION")
    print("=" * 50)
    print(f"Schema file: {os.path.abspath('supabase_schema.sql')}")
    
    if os.path.exists("supabase_schema.sql"):
        print("✅ Schema file exists")
        print("\nWould you like to see the schema content? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                show_schema()
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            return
    
    print("\n🎯 Next Steps:")
    print("1. Create the tables in Supabase Dashboard")
    print("2. Run: docker compose exec ragflow-backend python test_supabase_schema.py")
    print("3. Verify all tests pass")

if __name__ == "__main__":
    main()
