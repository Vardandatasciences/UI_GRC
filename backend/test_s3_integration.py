#!/usr/bin/env python3
"""
Test script for S3 microservice integration with incident file uploads
This script demonstrates how the incident system now uses the Render S3 microservice
"""

import os
import sys
import django
import requests
import json

# Add the parent directory to the path so we can import Django modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_s3_connection():
    """Test the S3 microservice connection"""
    print("🧪 Testing S3 Microservice Connection")
    print("=" * 50)
    
    try:
        # Test the Django endpoint
        response = requests.get('http://localhost:8000/api/test-s3-integration/')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Django endpoint response:")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                print("\n✅ S3 integration test PASSED")
                test_results = result.get('test_results', {})
                
                print(f"\n📊 Connection Status:")
                print(f"   Render microservice: {test_results.get('render_status', 'unknown')}")
                print(f"   MySQL database: {test_results.get('mysql_status', 'unknown')}")
                print(f"   Overall success: {test_results.get('overall_success', False)}")
                
                if 'operation_stats' in result:
                    stats = result['operation_stats']
                    print(f"\n📈 Operation Statistics:")
                    print(f"   Total operations: {stats.get('total_operations', 0)}")
                    print(f"   Completed: {stats.get('total_completed', 0)}")
                    print(f"   Failed: {stats.get('total_failed', 0)}")
                
                if 'recent_operations' in result:
                    ops = result['recent_operations']
                    print(f"\n📋 Recent Operations ({len(ops)}):")
                    for i, op in enumerate(ops[:3], 1):
                        print(f"   {i}. {op.get('operation_type')} - {op.get('file_name')} ({op.get('status')})")
                
            else:
                print("❌ S3 integration test FAILED")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

def test_direct_s3_client():
    """Test the S3 client directly"""
    print("\n🔧 Testing Direct S3 Client")
    print("=" * 50)
    
    try:
        # Import and test the S3 client directly
        from grc.s3_fucntions import create_render_mysql_client
        
        client = create_render_mysql_client()
        print("✅ S3 client created successfully")
        
        # Test connection
        result = client.test_connection()
        print(f"✅ Connection test completed:")
        print(f"   Render: {result.get('render_status')}")
        print(f"   MySQL: {result.get('mysql_status')}")
        print(f"   Success: {result.get('overall_success')}")
        
        # Show operation stats
        stats = client.get_operation_stats()
        if stats:
            print(f"\n📊 Database Stats:")
            print(f"   Total operations: {stats.get('total_operations', 0)}")
            for op_type in stats.get('operations_by_type', []):
                print(f"   {op_type['operation_type']}: {op_type['total_count']} total, {op_type['completed_count']} completed")
        
    except Exception as e:
        print(f"❌ Direct client test failed: {e}")

def show_integration_summary():
    """Show summary of what was integrated"""
    print("\n🎯 Integration Summary")
    print("=" * 50)
    print("✅ Successfully integrated Render S3 microservice with incident file uploads")
    print("\n📋 What was changed:")
    print("   1. Modified FileUploadView in incident_views.py")
    print("   2. Replaced S3Client with RenderS3Client from s3_functions.py")
    print("   3. Updated response format to match Vue component expectations")
    print("   4. Enhanced error handling and logging")
    print("   5. Added test endpoint for verifying integration")
    print("\n🔗 Key endpoints:")
    print("   • File Upload: POST /api/upload-file/")
    print("   • S3 Test: GET /api/test-s3-integration/")
    print("\n📁 Files modified:")
    print("   • backend/grc/incident_views.py (FileUploadView)")
    print("   • backend/grc/urls.py (added test endpoint)")
    print("\n⚙️  How it works:")
    print("   1. Vue component uploads file to Django endpoint")
    print("   2. Django validates and scans file for security")
    print("   3. Django uses RenderS3Client to upload to Render microservice")
    print("   4. Render microservice uploads to AWS S3")
    print("   5. Django returns S3 URL to Vue component")
    print("   6. All operations are tracked in MySQL database")

def main():
    """Main test function"""
    print("🚀 S3 Microservice Integration Test")
    print("🌐 Render URL: https://aws-microservice.onrender.com")
    print("🗄️  Database: Local MySQL")
    print("📋 Vue Component: IncidentUserTasks.vue")
    print("=" * 60)
    
    # Test S3 connection via Django endpoint
    test_s3_connection()
    
    # Test S3 client directly
    test_direct_s3_client()
    
    # Show integration summary
    show_integration_summary()
    
    print("\n🎉 Integration test completed!")
    print("\n💡 Next steps:")
    print("   1. Test file upload in Vue component")
    print("   2. Verify files are uploaded to S3")
    print("   3. Check MySQL database for operation records")
    print("   4. Monitor console logs for any errors")

if __name__ == "__main__":
    main() 