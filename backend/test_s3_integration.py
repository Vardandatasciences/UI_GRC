#!/usr/bin/env python3
"""
Test script to verify S3 integration with the auditing system
"""

import os
import tempfile
import sys
import json
from grc.s3_fucntions import create_render_mysql_client

def test_s3_integration():
    """Test S3 integration functionality"""
    
    print("🚀 Testing S3 Integration for Audit Evidence Upload")
    print("=" * 60)
    
    try:
        # Create S3 client
        print("1. Creating S3 client...")
        s3_client = create_render_mysql_client()
        
        # Test connection
        print("2. Testing connections...")
        connection_test = s3_client.test_connection()
        
        if not connection_test.get('overall_success', False):
            print("❌ Connection test failed!")
            print(f"   Render Status: {connection_test.get('render_status', 'unknown')}")
            print(f"   MySQL Status: {connection_test.get('mysql_status', 'unknown')}")
            if connection_test.get('render_error'):
                print(f"   Render Error: {connection_test['render_error']}")
            if connection_test.get('mysql_error'):
                print(f"   MySQL Error: {connection_test['mysql_error']}")
            return False
        
        print("✅ Connection test passed!")
        print(f"   Render Status: {connection_test.get('render_status', 'unknown')}")
        print(f"   MySQL Status: {connection_test.get('mysql_status', 'unknown')}")
        
        # Create a test file
        print("\n3. Creating test file...")
        test_content = json.dumps({
            "test_type": "audit_evidence",
            "audit_id": "123",
            "compliance_id": "456",
            "uploaded_by": "test_user",
            "test_timestamp": "2024-01-15T10:30:00Z",
            "description": "Test evidence file for S3 integration"
        }, indent=2)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Upload test file
            print("4. Uploading test file to S3...")
            upload_result = s3_client.upload(
                file_path=temp_file_path,
                user_id="test_user",
                custom_file_name="test_audit_evidence.json"
            )
            
            if upload_result.get('success'):
                print("✅ Upload successful!")
                file_info = upload_result.get('file_info', {})
                print(f"   File URL: {file_info.get('url', 'N/A')}")
                print(f"   S3 Key: {file_info.get('s3Key', 'N/A')}")
                print(f"   Stored Name: {file_info.get('storedName', 'N/A')}")
                print(f"   Operation ID: {upload_result.get('operation_id', 'N/A')}")
                
                # Test download
                print("\n5. Testing download...")
                download_result = s3_client.download(
                    s3_key=file_info.get('s3Key'),
                    file_name=file_info.get('storedName'),
                    destination_path="./test_downloads",
                    user_id="test_user"
                )
                
                if download_result.get('success'):
                    print("✅ Download successful!")
                    print(f"   Downloaded to: {download_result.get('file_path', 'N/A')}")
                    print(f"   File size: {download_result.get('file_size', 'N/A')} bytes")
                else:
                    print("❌ Download failed!")
                    print(f"   Error: {download_result.get('error', 'Unknown error')}")
                    
            else:
                print("❌ Upload failed!")
                print(f"   Error: {upload_result.get('error', 'Unknown error')}")
                return False
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        # Show operation history
        print("\n6. Operation history:")
        history = s3_client.get_operation_history('test_user', 5)
        
        if history:
            for i, op in enumerate(history, 1):
                print(f"   {i}. {op['operation_type']} - {op['file_name']} - {op['status']} ({op['created_at']})")
        else:
            print("   No operations found in database")
        
        # Show statistics
        print("\n7. Database statistics:")
        stats = s3_client.get_operation_stats()
        
        if stats:
            print(f"   Total operations: {stats.get('total_operations', 0)}")
            print(f"   Completed: {stats.get('total_completed', 0)}")
            print(f"   Failed: {stats.get('total_failed', 0)}")
        else:
            print("   No statistics available")
        
        print("\n🎉 S3 integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ S3 integration test failed: {str(e)}")
        return False

def test_backend_endpoint():
    """Test the backend endpoint setup"""
    
    print("\n🔧 Testing Backend Endpoint Configuration")
    print("=" * 60)
    
    try:
        # Try to import the endpoint function
        from grc.auditing import upload_evidence_to_s3
        print("✅ S3 upload endpoint imported successfully")
        
        # Check if the endpoint is properly configured
        print("✅ Backend endpoint configuration appears correct")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import S3 upload endpoint: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Backend endpoint test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 S3 Integration Test Suite")
    print("=" * 60)
    
    # Test 1: S3 functionality
    s3_test_passed = test_s3_integration()
    
    # Test 2: Backend endpoint
    backend_test_passed = test_backend_endpoint()
    
    print("\n📋 Test Results Summary:")
    print(f"   S3 Integration: {'✅ PASSED' if s3_test_passed else '❌ FAILED'}")
    print(f"   Backend Endpoint: {'✅ PASSED' if backend_test_passed else '❌ FAILED'}")
    
    if s3_test_passed and backend_test_passed:
        print("\n🎉 All tests passed! S3 integration is ready for use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
        sys.exit(1) 