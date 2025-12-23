#!/usr/bin/env python3
"""
Test script to verify enhanced 401 unauthorized categorization
"""

import sys
import os

# Add the src directory to path
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
src_dir = os.path.join(current_dir, 'src')
utils_dir = os.path.join(src_dir, 'utils')
sys.path.insert(0, src_dir)
sys.path.insert(0, utils_dir)

# Import our enhanced analyzer
sys.path.append(utils_dir)
import local_analyzer_enhanced

def test_401_categorization():
    """Test 401 unauthorized categorization"""
    
    print("🧪 Testing Enhanced 401 Unauthorized Categorization")
    print("=" * 60)
    
    # Initialize enhanced analyzer
    analyzer = local_analyzer_enhanced.EnhancedAnalyzer()
    
    # Test cases for 401 unauthorized
    test_cases = [
        {
            'name': 'HTTP 401 Basic',
            'failure_reason': 'HTTP Error 401: Unauthorized access to /api/users endpoint'
        },
        {
            'name': 'Authentication Failed with 401',
            'failure_reason': 'Authentication failed - HTTP 401 Unauthorized. Token may be expired.'
        },
        {
            'name': 'API 401 Response',
            'failure_reason': 'API call failed with 401 unauthorized - invalid credentials'
        },
        {
            'name': 'Generic Unauthorized',
            'failure_reason': 'Unauthorized access denied'
        },
        {
            'name': '403 Forbidden Test',
            'failure_reason': 'HTTP Error 403: Forbidden - insufficient permissions'
        },
        {
            'name': 'Network 404 Error',
            'failure_reason': 'HTTP 404 Not Found: API endpoint /api/v2/users not found'
        },
        {
            'name': 'Server 500 Error',
            'failure_reason': 'HTTP 500 Internal Server Error: Database connection failed'
        }
    ]
    
    print(f"Testing {len(test_cases)} failure scenarios:\n")
    
    for i, test_case in enumerate(test_cases, 1):
        result = analyzer.categorize_failure(test_case['failure_reason'])
        
        print(f"{i}. {test_case['name']}")
        print(f"   Failure: {test_case['failure_reason']}")
        print(f"   ✅ Category: {result['category']}")
        print(f"   ✅ Confidence: {result['confidence']:.0%}")
        print(f"   ✅ Hint: {result['hint']}")
        if 'http_status' in result:
            print(f"   ✅ HTTP Status: {result['http_status']}")
        print()
    
    # Test environment mapping
    print("🌍 Testing Environment Mapping:")
    print("-" * 40)
    
    env_tests = [
        'staging-api-server',
        'dev-linuxaa8d0014O1',
        'prod-api-gateway',
        'qa-server-east-region'
    ]
    
    for env in env_tests:
        mapped = analyzer.map_environment(env)
        print(f"   {env} → {mapped}")
    
    print("\n✅ Enhanced categorization test completed!")

if __name__ == "__main__":
    test_401_categorization()