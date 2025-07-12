#!/usr/bin/env python3
"""
Simple test script to verify policy document upload functionality
"""

import requests
import os
import tempfile

def test_upload_endpoint():
    """Test the upload policy document endpoint"""
    
    print("🧪 Testing Policy Document Upload Endpoint")
    print("=" * 50)
    
    # Create a test file
    test_content = "Test policy document content"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        # Prepare the file for upload
        with open(temp_file_path, 'rb') as test_file:
            files = {
                'file': ('test_policy.txt', test_file, 'text/plain')
            }
            
            data = {
                'userId': 'test_user',
                'fileName': 'test_policy.txt',
                'type': 'policy',
                'policyName': 'Test Policy'
            }
            
            # Make the upload request
            print("📤 Uploading test file...")
            response = requests.post(
                'http://localhost:8000/api/upload-policy-document/',
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Upload successful!")
                    print(f"File URL: {result['file']['url']}")
                    print(f"Stored Name: {result['file']['storedName']}")
                    return True
                else:
                    print(f"❌ Upload failed: {result.get('error')}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    success = test_upload_endpoint()
    if success:
        print("\n🎉 Upload endpoint test passed!")
    else:
        print("\n❌ Upload endpoint test failed!")
        print("\n💡 Make sure:")
        print("   - Django server is running (python manage.py runserver)")
        print("   - S3 service is properly configured")
        print("   - Required dependencies are installed") 