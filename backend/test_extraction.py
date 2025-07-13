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
from grc.routes.final_adithya import (
    extract_document_sections, 
    find_toc_page, 
    extract_text_with_styles_from_pages, 
    get_num_pages
)

def test_pdf_extraction():
    """Test PDF extraction functions directly"""
    media_root = settings.MEDIA_ROOT
    framework_uploads_dir = os.path.join(media_root, 'framework_uploads')
    
    # Find the latest upload directory
    upload_dirs = [d for d in os.listdir(framework_uploads_dir) if os.path.isdir(os.path.join(framework_uploads_dir, d))]
    if not upload_dirs:
        print("No upload directories found")
        return
    
    # Use the most recent upload directory
    latest_upload_dir = sorted(upload_dirs)[-1]
    print(f"Testing with upload directory: {latest_upload_dir}")
    
    upload_path = os.path.join(framework_uploads_dir, latest_upload_dir)
    pdf_files = [f for f in os.listdir(upload_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found")
        return
    
    pdf_path = os.path.join(upload_path, pdf_files[0])
    print(f"Testing PDF: {pdf_path}")
    
    # Test each function
    try:
        print("\n=== Testing get_num_pages ===")
        num_pages = get_num_pages(pdf_path)
        print(f"Number of pages: {num_pages}")
        
        print("\n=== Testing find_toc_page ===")
        toc_page = find_toc_page(pdf_path)
        print(f"TOC page: {toc_page}")
        
        print("\n=== Testing extract_text_with_styles_from_pages ===")
        text_data = extract_text_with_styles_from_pages(pdf_path, 1, min(10, num_pages))  # Test first 10 pages
        print(f"Extracted {len(text_data) if text_data else 0} text elements")
        
        print("\n=== Testing extract_document_sections ===")
        output_dir = os.path.join(media_root, 'extracted_sections', 'test_extraction')
        os.makedirs(output_dir, exist_ok=True)
        
        task_id = "test_task"
        sections = extract_document_sections(pdf_path, output_dir, task_id)
        print(f"Extracted sections: {sections}")
        
        # Check what was created
        if os.path.exists(output_dir):
            print(f"Output directory contents: {os.listdir(output_dir)}")
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                if os.path.isdir(item_path):
                    print(f"Directory {item}: {os.listdir(item_path)}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_extraction() 