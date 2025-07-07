#!/usr/bin/env python3
"""
Test script for S3 integration with the file upload system.
This script tests the complete flow from file upload to S3 storage.
"""
import os
import sys
import django
import requests
import json
import tempfile
from pathlib import Path

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from grc.s3_fucntions import S3Client
from grc.incident_views import FileUploadView

class S3IntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.s3_client = S3Client()
        
    def test_s3_service_health(self):
        """Test if S3 microservice is running"""
        print("🔍 Testing S3 service health...")
        
        health_check = self.s3_client.check_health()
        
        if health_check.get('is_running'):
            print("✅ S3 microservice is running")
            print(f"   Status: {health_check.get('message', 'OK')}")
            return True
        else:
            print("❌ S3 microservice is not running")
            print(f"   Error: {health_check.get('message', 'Unknown error')}")
            return False
    
    def test_file_upload_endpoint(self):
        """Test the file upload endpoint"""
        print("\n🔍 Testing file upload endpoint...")
        
        # Create a test file
        test_content = "This is a test file for S3 integration testing."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Prepare test data
            files = {'file': ('test_file.txt', open(temp_file_path, 'rb'), 'text/plain')}
            data = {
                'incidentId': '1',
                'mitigationNumber': '1',
                'userId': '1',
                'itemType': 'incident',
                'uploadType': 'mitigation_evidence'
            }
            
            # Make request to upload endpoint
            response = requests.post(
                f"{self.base_url}/api/upload-file/",
                files=files,
                data=data
            )
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    print("✅ File upload successful")
                    print(f"   S3 URL: {response_data.get('file_url', 'Not provided')}")
                    print(f"   File ID: {response_data.get('file_id', 'Not provided')}")
                    return True, response_data
                else:
                    print("❌ File upload failed")
                    print(f"   Error: {response_data.get('error', 'Unknown error')}")
                    return False, response_data
            else:
                print("❌ File upload failed")
                print(f"   HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, None
                
        finally:
            # Clean up test file
            files['file'][1].close()
            os.unlink(temp_file_path)
    
    def test_direct_s3_upload(self):
        """Test direct S3 upload using S3Client"""
        print("\n🔍 Testing direct S3 upload...")
        
        # Create a test file
        test_content = "This is a direct S3 upload test file."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Upload using S3Client directly
            upload_result = self.s3_client.upload_file(
                file_path=temp_file_path,
                user_id="test_user",
                file_name="direct_test.txt",
                incident_id="test_incident",
                mitigation_number="1",
                upload_type="test"
            )
            
            if upload_result.get('success'):
                print("✅ Direct S3 upload successful")
                print(f"   S3 URL: {upload_result['file']['url']}")
                print(f"   File ID: {upload_result['file']['id']}")
                return True, upload_result
            else:
                print("❌ Direct S3 upload failed")
                print(f"   Error: {upload_result}")
                return False, upload_result
                
        except Exception as e:
            print("❌ Direct S3 upload failed")
            print(f"   Exception: {str(e)}")
            return False, None
        finally:
            # Clean up test file
            os.unlink(temp_file_path)
    
    def test_s3_health_endpoint(self):
        """Test the S3 health check endpoint"""
        print("\n🔍 Testing S3 health check endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/api/incidents/s3-health/")
            
            if response.status_code == 200:
                response_data = response.json()
                print("✅ S3 health endpoint working")
                print(f"   S3 Running: {response_data.get('is_running')}")
                print(f"   Message: {response_data.get('message')}")
                return True, response_data
            else:
                print("❌ S3 health endpoint failed")
                print(f"   HTTP Error: {response.status_code}")
                return False, None
                
        except Exception as e:
            print("❌ S3 health endpoint failed")
            print(f"   Exception: {str(e)}")
            return False, None
    
    def test_file_download(self, file_id):
        """Test file download from S3"""
        print(f"\n🔍 Testing file download for file ID: {file_id}...")
        
        try:
            # Create download directory
            download_dir = Path("test_downloads")
            download_dir.mkdir(exist_ok=True)
            
            # Download file
            downloaded_path = self.s3_client.download_file(file_id, str(download_dir))
            
            if downloaded_path and Path(downloaded_path).exists():
                print("✅ File download successful")
                print(f"   Downloaded to: {downloaded_path}")
                
                # Read and verify content
                with open(downloaded_path, 'r') as f:
                    content = f.read()
                    print(f"   Content preview: {content[:100]}...")
                
                # Clean up
                os.unlink(downloaded_path)
                return True
            else:
                print("❌ File download failed")
                return False
                
        except Exception as e:
            print("❌ File download failed")
            print(f"   Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting S3 Integration Tests")
        print("=" * 50)
        
        results = {}
        
        # Test 1: S3 Service Health
        results['s3_health'] = self.test_s3_service_health()
        
        # Test 2: S3 Health Endpoint
        results['health_endpoint'] = self.test_s3_health_endpoint()[0]
        
        # Test 3: Direct S3 Upload
        direct_result, direct_data = self.test_direct_s3_upload()
        results['direct_upload'] = direct_result
        
        # Test 4: File Upload Endpoint
        upload_result, upload_data = self.test_file_upload_endpoint()
        results['upload_endpoint'] = upload_result
        
        # Test 5: File Download (if we have a file ID)
        if direct_result and direct_data:
            file_id = direct_data['file']['id']
            results['file_download'] = self.test_file_download(file_id)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! S3 integration is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the S3 microservice and configuration.")
        
        return results

def main():
    """Main function to run tests"""
    tester = S3IntegrationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 