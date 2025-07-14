#!/usr/bin/env python3
"""
Simple script to help set up OpenAI API key for the GRC system.
"""

import os
import sys

def setup_openai_key():
    """Set up OpenAI API key in environment variables."""
    
    print("=== OpenAI API Key Setup ===")
    print()
    
    # Check if API key is already set
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        print(f"✅ OpenAI API key is already set: {current_key[:8]}...")
        print("You can proceed with using the AI analysis features.")
        return True
    
    print("❌ OpenAI API key not found in environment variables.")
    print()
    print("To use AI-powered incident analysis, you need to:")
    print("1. Get an OpenAI API key from https://platform.openai.com/api-keys")
    print("2. Set it as an environment variable")
    print()
    
    # Ask user if they want to set it now
    try:
        choice = input("Do you want to set your OpenAI API key now? (y/n): ").lower().strip()
        
        if choice in ['y', 'yes']:
            api_key = input("Enter your OpenAI API key: ").strip()
            
            if api_key:
                # Set the environment variable for current session
                os.environ['OPENAI_API_KEY'] = api_key
                print("✅ API key set for current session!")
                print("Note: This will only work for the current terminal session.")
                print("For permanent setup, add this to your environment variables:")
                print(f"set OPENAI_API_KEY={api_key}")
                return True
            else:
                print("❌ No API key provided.")
                return False
        else:
            print("You can set the API key later by running:")
            print("set OPENAI_API_KEY=your_api_key_here")
            return False
            
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        return False

def test_openai_connection():
    """Test if OpenAI connection works."""
    try:
        from langchain_community.chat_models import ChatOpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ No OpenAI API key found.")
            return False
        
        # Test with a simple call
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key,
            max_tokens=100
        )
        
        response = llm.invoke("Say 'Hello, OpenAI is working!'")
        print("✅ OpenAI connection successful!")
        print(f"Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

if __name__ == "__main__":
    print("OpenAI Setup for GRC System")
    print("=" * 40)
    
    if setup_openai_key():
        print("\nTesting connection...")
        test_openai_connection()
    
    print("\nSetup complete!") 