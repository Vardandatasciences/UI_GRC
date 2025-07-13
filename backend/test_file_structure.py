#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def check_file_structure():
    """Check the current file structure in MEDIA_ROOT"""
    media_root = settings.MEDIA_ROOT
    print(f"MEDIA_ROOT: {media_root}")
    
    if not os.path.exists(media_root):
        print(f"ERROR: MEDIA_ROOT does not exist: {media_root}")
        return
    
    print(f"MEDIA_ROOT exists: {media_root}")
    print(f"MEDIA_ROOT contents: {os.listdir(media_root)}")
    
    # Check framework_uploads
    framework_uploads_dir = os.path.join(media_root, 'framework_uploads')
    if os.path.exists(framework_uploads_dir):
        print(f"framework_uploads exists: {framework_uploads_dir}")
        upload_dirs = os.listdir(framework_uploads_dir)
        print(f"Upload directories: {upload_dirs}")
        
        for upload_dir in upload_dirs:
            upload_path = os.path.join(framework_uploads_dir, upload_dir)
            if os.path.isdir(upload_path):
                files = os.listdir(upload_path)
                print(f"Files in {upload_dir}: {files}")
    else:
        print(f"framework_uploads does not exist: {framework_uploads_dir}")
    
    # Check extracted_sections
    extracted_sections_dir = os.path.join(media_root, 'extracted_sections')
    if os.path.exists(extracted_sections_dir):
        print(f"extracted_sections exists: {extracted_sections_dir}")
        extracted_dirs = os.listdir(extracted_sections_dir)
        print(f"Extracted directories: {extracted_dirs}")
        
        for extracted_dir in extracted_dirs:
            extracted_path = os.path.join(extracted_sections_dir, extracted_dir)
            if os.path.isdir(extracted_path):
                contents = os.listdir(extracted_path)
                print(f"Contents in {extracted_dir}: {contents}")
    else:
        print(f"extracted_sections does not exist: {extracted_sections_dir}")
        # Create it
        os.makedirs(extracted_sections_dir, exist_ok=True)
        print(f"Created extracted_sections directory: {extracted_sections_dir}")

if __name__ == "__main__":
    check_file_structure() 