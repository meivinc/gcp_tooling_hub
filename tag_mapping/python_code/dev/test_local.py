#!/usr/bin/env python3
"""
Local testing script for the Cloud Function
"""
import os
import sys
from main import tags_to_bigquery_function

# Mock HTTP request for testing
class MockRequest:
    def __init__(self):
        self.method = 'POST'
        self.data = b'{}'
        self.headers = {}

def test_local():
    """Test the function locally with environment variables."""
    print("🧪 Testing Cloud Function locally...")
    print("=" * 50)
    
    # Configuration will be loaded from config.py or environment variables
    print("Configuration will be loaded from:")
    print("  1. Environment variables (if set)")
    print("  2. config.py file (if exists)")
    print("  3. Default values (fallback)")
    print()
    
    try:
        # Create mock HTTP request
        mock_request = MockRequest()
        
        # Run the function
        result = tags_to_bigquery_function(mock_request)
        
        print("✅ Function completed!")
        print("Result:", result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_local()