#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.urls import reverse
from django.test import Client

def test_url_patterns():
    """Test if the URL patterns are working correctly."""
    client = Client()
    
    # Test the get-sections URL pattern
    task_id = "test_task_123"
    url = f'/api/get-sections/{task_id}/'
    
    print(f"Testing URL: {url}")
    
    try:
        response = client.get(url)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content[:200]}...")
    except Exception as e:
        print(f"Error testing URL: {e}")

if __name__ == "__main__":
    test_url_patterns() 