#!/usr/bin/env python3
"""
Simple Test for Enhanced Features
Tests core enhancement logic without complex imports
"""

import json
import re
from typing import Dict, Any, List

# Environment mapping patterns
ENVIRONMENT_MAPPING = {
    r'dev.*linux.*': 'dev',
    r'qa.*server.*': 'qa', 
    r'staging.*': 'staging',
    r'prod.*': 'production',
    r'.*unittest.*': 'dev',
    r'.*performance.*': 'staging'
}

# Enhanced failure categorization patterns
ENHANCED_PATTERNS = {
    'authentication_failure': {
        'patterns': [
            r'authentication.*failed',
            r'invalid.*credentials',
            r'login.*failed',
            r'unauthorized',
            r'401.*error'
        ],
        'hints': [
            "Check authentication service status and user credentials",
            "Verify test data includes valid login information",
            "Review authentication flow for recent changes"
        ]
    },
    'timeout_performance': {
        'patterns': [
            r'timeout.*exceeded',
            r'page.*did.*not.*load',
            r'wait.*timeout',
            r'performance.*threshold.*exceeded'
        ],
        'hints': [
            "Investigate page load performance and optimize slow elements",
            "Increase timeout values if performance degradation is expected",
            "Check network connectivity and server response times"
        ]
    },
    'network_api_error': {
        'patterns': [
            r'network.*error',
            r'failed.*to.*fetch',
            r'connection.*refused',
            r'api.*endpoint.*error',
            r'http.*error.*[45]\d{2}'
        ],
        'hints': [
            "Verify API endpoint availability and correct URLs",
            "Check network connectivity and firewall settings",
            "Review API service logs for errors"
        ]
    },
    'element_interaction': {
        'patterns': [
            r'element.*not.*found',
            r'selector.*not.*found',
            r'cannot.*locate.*element',
            r'element.*not.*visible'
        ],
        'hints': [
            "Check if page elements have changed (selectors, IDs, classes)",
            "Verify page loads completely before element interaction",
            "Update element selectors if UI has been modified"
        ]
    },
    'data_validation': {
        'patterns': [
            r'expected.*but.*got',
            r'assertion.*failed',
            r'value.*mismatch',
            r'data.*validation.*failed'
        ],
        'hints': [
            "Review test data setup and ensure correct values",
            "Check for data dependencies and prerequisites",
            "Verify database state and test data isolation"
        ]
    }
}

def map_environment(raw_environment: str) -> str:
    """Map raw environment string to logical environment"""
    if not raw_environment:
        return 'unknown'
    
    raw_env_lower = raw_environment.lower()
    
    for pattern, mapped_env in ENVIRONMENT_MAPPING.items():
        if re.search(pattern, raw_env_lower):
            return mapped_env
    
    return 'unknown'

def categorize_failure(failure_reason: str) -> Dict[str, Any]:
    """Enhanced failure categorization with specific hints"""
    if not failure_reason:
        return {
            'category': 'unknown',
            'confidence': 0.0,
            'hint': 'No failure reason provided',
            'reasoning': 'Cannot categorize without failure details'
        }
    
    failure_lower = failure_reason.lower()
    
    for category, category_data in ENHANCED_PATTERNS.items():
        for pattern in category_data['patterns']:
            if re.search(pattern, failure_lower):
                return {
                    'category': category,
                    'confidence': 0.85,
                    'hint': category_data['hints'][0],  # Primary hint
                    'reasoning': f"Matched pattern: {pattern}",
                    'all_hints': category_data['hints']
                }
    
    return {
        'category': 'unknown',
        'confidence': 0.0,
        'hint': 'Manual investigation needed - pattern not recognized',
        'reasoning': 'No known failure patterns matched'
    }

def enhance_test_result(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance a single test result with categorization and environment mapping"""
    enhanced = test_data.copy()
    
    # Map environment
    raw_env = test_data.get('environment', 'unknown')
    enhanced['environment'] = map_environment(raw_env)
    enhanced['environment_source'] = raw_env
    
    # Enhanced categorization for failed tests
    if test_data.get('status') == 'failed':
        failure_reason = test_data.get('failure_reason', '')
        categorization = categorize_failure(failure_reason)
        
        enhanced['failure_category'] = categorization['category']
        enhanced['confidence_score'] = categorization['confidence']
        enhanced['failure_hint'] = categorization['hint']
        enhanced['category_reasoning'] = categorization['reasoning']
    else:
        enhanced['failure_category'] = 'n/a'
        enhanced['confidence_score'] = 1.0
        enhanced['failure_hint'] = 'Test passed successfully'
        enhanced['category_reasoning'] = 'No failure to categorize'
    
    return enhanced

def test_enhancements():
    """Test the enhancement functions"""
    print("🧪 Testing Enhanced Categorization and Environment Mapping")
    print("=" * 70)
    
    # Test data
    test_cases = [
        {
            'test_name': 'login_auth_test',
            'status': 'failed',
            'failure_reason': 'Authentication failed: Invalid credentials provided',
            'environment': 'dev-linuxaa8d0014O1',
            'duration': 5500
        },
        {
            'test_name': 'page_timeout_test', 
            'status': 'failed',
            'failure_reason': 'Timeout: Page did not load within 30 seconds',
            'environment': 'qa-server-east-region',
            'duration': 32000
        },
        {
            'test_name': 'api_error_test',
            'status': 'failed', 
            'failure_reason': 'Network error: Failed to fetch data from API endpoint',
            'environment': 'staging-webserver01',
            'duration': 8000
        },
        {
            'test_name': 'successful_test',
            'status': 'passed',
            'failure_reason': None,
            'environment': 'qa-server-west',
            'duration': 4500
        },
        {
            'test_name': 'element_test',
            'status': 'failed',
            'failure_reason': 'Element with selector .submit-button not found',
            'environment': 'prod-loadbalancer',
            'duration': 12000
        }
    ]
    
    results = []
    improvements = {'unknown_before': 0, 'unknown_after': 0}
    
    for test in test_cases:
        print(f"\n🔍 Testing: {test['test_name']}")
        
        # Track before enhancement
        original_category = test.get('failure_category', 'unknown' if test['status'] == 'failed' else 'n/a')
        if original_category in ['unknown', 'other'] and test['status'] == 'failed':
            improvements['unknown_before'] += 1
        
        # Enhance the test
        enhanced = enhance_test_result(test)
        results.append(enhanced)
        
        # Track after enhancement
        new_category = enhanced.get('failure_category', 'unknown')
        if new_category in ['unknown', 'other'] and test['status'] == 'failed':
            improvements['unknown_after'] += 1
        
        print(f"   Original Environment: {test.get('environment', 'N/A')}")
        print(f"   Mapped Environment: {enhanced.get('environment')}")
        
        if test['status'] == 'failed':
            print(f"   Failure Category: {enhanced.get('failure_category')}")
            print(f"   Confidence: {enhanced.get('confidence_score', 0):.2f}")
            print(f"   Hint: {enhanced.get('failure_hint')}")
            print(f"   Reasoning: {enhanced.get('category_reasoning')}")
    
    # Calculate improvements
    improvements['improvement_count'] = improvements['unknown_before'] - improvements['unknown_after']
    total_failed = sum(1 for test in test_cases if test['status'] == 'failed')
    improvements['improvement_percentage'] = (improvements['improvement_count'] / total_failed * 100) if total_failed > 0 else 0
    
    print(f"\n📊 Enhancement Results:")
    print(f"   Tests Processed: {len(test_cases)}")
    print(f"   Failed Tests: {total_failed}")
    print(f"   Unknown Categories Before: {improvements['unknown_before']}")
    print(f"   Unknown Categories After: {improvements['unknown_after']}")
    print(f"   Categories Resolved: {improvements['improvement_count']}")
    print(f"   Improvement Rate: {improvements['improvement_percentage']:.1f}%")
    
    # Performance analysis simulation
    print(f"\n⚡ Performance Analysis:")
    durations = [test['duration'] for test in test_cases]
    avg_duration = sum(durations) / len(durations)
    fast_tests = sum(1 for d in durations if d < 5000)
    slow_tests = sum(1 for d in durations if d > 30000)
    
    print(f"   Average Duration: {avg_duration:.1f}ms ({avg_duration/1000:.1f}s)")
    print(f"   Fast Tests (<5s): {fast_tests} ({fast_tests/len(test_cases)*100:.1f}%)")
    print(f"   Slow Tests (>30s): {slow_tests} ({slow_tests/len(test_cases)*100:.1f}%)")
    
    # Environment distribution
    print(f"\n🌍 Environment Distribution:")
    env_counts = {}
    for result in results:
        env = result.get('environment', 'unknown')
        env_counts[env] = env_counts.get(env, 0) + 1
    
    for env, count in sorted(env_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(results)) * 100
        print(f"   {env.capitalize()}: {count} tests ({percentage:.1f}%)")
    
    # Top insights
    print(f"\n💡 Top Actionable Insights:")
    insights = []
    for result in results:
        if result.get('status') == 'failed' and result.get('failure_hint'):
            insights.append({
                'test': result['test_name'],
                'category': result.get('failure_category', 'unknown'),
                'hint': result.get('failure_hint'),
                'environment': result.get('environment')
            })
    
    for i, insight in enumerate(insights[:3], 1):
        print(f"   {i}. {insight['test']} ({insight['category']}):")
        print(f"      {insight['hint']}")
        print(f"      Environment: {insight['environment']}")
    
    print("\n✅ Enhanced analysis testing completed successfully!")
    return results, improvements

if __name__ == "__main__":
    test_enhancements()