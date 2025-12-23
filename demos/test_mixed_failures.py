#!/usr/bin/env python3
"""
Test mixed failures to verify both enhanced 401 categorization and original pattern matching work together
"""

import sys
import os
import json

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.enhanced_analyzer import EnhancedLocalAnalyzer

def test_mixed_failures():
    """Test analyzer with various failure types to ensure comprehensive categorization"""
    
    # Sample test data with mixed failure types
    test_data = [
        # 401 Unauthorized (should use enhanced categorization)
        {
            'test_name': 'test_user_login',
            'status': 'FAIL',
            'error_message': 'HTTP 401 Unauthorized: Authentication failed for user credentials',
            'environment': 'uat'
        },
        # 403 Forbidden (should use enhanced categorization)
        {
            'test_name': 'test_admin_access',
            'status': 'FAIL', 
            'error_message': 'HTTP 403 Forbidden: Insufficient permissions to access resource',
            'environment': 'prod'
        },
        # Element not found (should use original categorization)
        {
            'test_name': 'test_click_button',
            'status': 'FAIL',
            'error_message': 'ElementNotInteractableException: Element not visible on page',
            'environment': 'dev'
        },
        # Timeout (should use original categorization)
        {
            'test_name': 'test_page_load',
            'status': 'FAIL',
            'error_message': 'TimeoutException: Page failed to load within 30 seconds',
            'environment': 'staging'
        },
        # Network error (should use original categorization)
        {
            'test_name': 'test_api_call',
            'status': 'FAIL',
            'error_message': 'ConnectionError: Failed to establish connection to server',
            'environment': 'qa'
        },
        # 500 Internal Server Error (should use enhanced categorization)
        {
            'test_name': 'test_server_response',
            'status': 'FAIL',
            'error_message': 'HTTP 500 Internal Server Error: Server processing failed',
            'environment': 'uat'
        }
    ]
    
    print("🧪 Testing Mixed Failure Categories")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = EnhancedLocalAnalyzer()
    
    # Analyze each failure
    for i, test in enumerate(test_data, 1):
        print(f"\n📋 Test {i}: {test['test_name']}")
        print(f"   Error: {test['error_message']}")
        
        # Get categorization
        result = analyzer.categorize_failure(test['error_message'])
        
        print(f"   🏷️  Category: {result['category']}")
        print(f"   🎯 Confidence: {result['confidence']:.0%}")
        print(f"   💡 Hint: {result['hint']}")
        print(f"   🔍 Reasoning: {result['reasoning']}")

    print("\n" + "=" * 60)
    print("✅ Mixed failure categorization test completed!")
    print("\nExpected Results:")
    print("- 401 errors: authentication_failure (95% confidence)")
    print("- 403 errors: authorization_failure (95% confidence)")  
    print("- Element issues: ui_interaction_failure (85% confidence)")
    print("- Timeouts: performance_issue (80% confidence)")
    print("- Network errors: connectivity_issue (85% confidence)")
    print("- 500 errors: server_error (90% confidence)")

if __name__ == "__main__":
    test_mixed_failures()