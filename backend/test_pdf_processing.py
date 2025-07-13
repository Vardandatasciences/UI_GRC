#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from grc.routes.final_adithya import (
    extract_document_sections, 
    find_toc_page, 
    extract_text_with_styles_from_pages, 
    get_num_pages
)

def test_pdf_functions():
    """Test if the PDF processing functions are working correctly."""
    
    # Test with a sample PDF file if it exists
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'backend', 'upload_1752143795_NIST.SP.800-53r5.pdf', 'NIST.SP.800-53r5.pdf')
    
    if os.path.exists(test_pdf_path):
        print(f"Testing PDF processing with: {test_pdf_path}")
        
        try:
            # Test get_num_pages
            num_pages = get_num_pages(test_pdf_path)
            print(f"Number of pages: {num_pages}")
            
            # Test find_toc_page
            toc_page = find_toc_page(test_pdf_path)
            print(f"Table of contents page: {toc_page}")
            
            # Test extract_text_with_styles_from_pages (first 2 pages only for speed)
            print("Extracting text with styles from first 2 pages...")
            text_data = extract_text_with_styles_from_pages(test_pdf_path, 1, min(2, num_pages))
            print(f"Extracted {len(text_data)} text elements")
            
            # Test extract_document_sections (with a small output dir)
            output_dir = os.path.join(os.path.dirname(__file__), 'test_output')
            print(f"Testing document section extraction to: {output_dir}")
            
            sections = extract_document_sections(test_pdf_path, output_dir, "test_task_123")
            print(f"Extracted {len(sections)} sections")
            
            print("✅ All PDF processing functions are working correctly!")
            
        except Exception as e:
            print(f"❌ Error testing PDF functions: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Test PDF file not found at: {test_pdf_path}")
        print("Please ensure the test PDF file exists for testing.")

if __name__ == "__main__":
    test_pdf_functions() 