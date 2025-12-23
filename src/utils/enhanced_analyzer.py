#!/usr/bin/env python3
"""
Enhanced Local Analyzer with Built-in HTTP Status Code Categorization
Provides specialized handling for 401/403 errors alongside comprehensive failure pattern matching
"""

import re
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime


class EnhancedLocalAnalyzer:
    """
    Enhanced test analyzer with built-in HTTP status code categorization
    and comprehensive failure pattern matching
    """

    def __init__(self):
        """Initialize the enhanced analyzer with failure patterns and HTTP status mapping"""

        # Environment mapping
        self.environment_mappings = {
            # Development environments
            'dev': 'Development',
            'development': 'Development',
            'local': 'Development',
            'localhost': 'Development',

            # Testing environments
            'test': 'Testing',
            'testing': 'Testing',
            'qa': 'Testing',
            'qe': 'Testing',
            'uat': 'User Acceptance Testing',
            'staging': 'Staging',
            'stage': 'Staging',
            'sit': 'System Integration Testing',

            # Production environments
            'prod': 'Production',
            'production': 'Production',
            'live': 'Production',

            # Fallback
            'unknown': 'Unknown Environment'
        }

        # Comprehensive failure patterns with confidence levels
        self.failure_patterns = {
            'ui_interaction_failure': {
                'patterns': [
                    r'ElementNotInteractableException',
                    r'ElementNotVisibleException',
                    r'NoSuchElementException',
                    r'StaleElementReferenceException',
                    r'element not found',
                    r'element not clickable',
                    r'element not visible',
                    r'could not locate element'
                ],
                'confidence': 0.85,
                'hints': [
                    'Check element selectors and wait conditions',
                    'Verify page load timing and dynamic content',
                    'Review element interaction timing'
                ]
            },

            'performance_issue': {
                'patterns': [
                    r'TimeoutException',
                    r'timeout',
                    r'response too slow',
                    r'page load timeout',
                    r'operation timed out'
                ],
                'confidence': 0.80,
                'hints': [
                    'Optimize page load times or increase timeout values',
                    'Check network connectivity and server response',
                    'Review application performance'
                ]
            },

            'connectivity_issue': {
                'patterns': [
                    r'ConnectionError',
                    r'NetworkError',
                    r'connection refused',
                    r'connection timeout',
                    r'host not found',
                    r'dns resolution failed'
                ],
                'confidence': 0.85,
                'hints': [
                    'Verify network connectivity and server availability',
                    'Check firewall and proxy settings',
                    'Validate service endpoints and URLs'
                ]
            },

            'data_validation_failure': {
                'patterns': [
                    r'AssertionError',
                    r'assertion failed',
                    r'expected.*but was',
                    r'value mismatch',
                    r'validation failed'
                ],
                'confidence': 0.90,
                'hints': [
                    'Review test data and expected values',
                    'Check data transformation and processing logic',
                    'Validate data sources and formats'
                ]
            },

            'server_error': {
                'patterns': [
                    r'HTTP [45]\d\d',
                    r'Internal Server Error',
                    r'Bad Gateway',
                    r'Service Unavailable',
                    r'server error'
                ],
                'confidence': 0.75,  # Lower than specific HTTP status detection
                'hints': [
                    'Check server logs and application status',
                    'Verify service dependencies and configurations',
                    'Review recent deployments or changes'
                ]
            },

            'configuration_issue': {
                'patterns': [
                    r'ConfigurationError',
                    r'configuration.*missing',
                    r'property.*not found',
                    r'invalid configuration',
                    r'config.*error'
                ],
                'confidence': 0.85,
                'hints': [
                    'Review application configuration files',
                    'Verify environment-specific settings',
                    'Check configuration management system'
                ]
            }
        }

    def extract_http_status_code(self, error_message: str) -> Optional[str]:
        """Extract HTTP status code from error message"""
        # Pattern 1: "HTTP 401" or "HTTP/1.1 401"
        http_pattern = r'HTTP[/\d.]?\s+(\d{3})'
        match = re.search(http_pattern, error_message, re.IGNORECASE)
        if match:
            return match.group(1)

        # Pattern 2: "401 -" or "failed: 401" (common in API error messages)
        status_pattern = r'(?:failed:|status:)?\s*(\d{3})\s*[-:]'
        match = re.search(status_pattern, error_message, re.IGNORECASE)
        if match:
            status = match.group(1)
            # Verify it's a valid HTTP status code (4xx or 5xx)
            if status.startswith(('4', '5')):
                return status

        return None

    def categorize_failure(self, error_message: str) -> Dict[str, Any]:
        """
        Categorize failure with enhanced HTTP status code detection and original pattern matching

        Args:
            error_message: The error message to categorize

        Returns:
            Dictionary with category, confidence, hint, and reasoning
        """
        if not error_message:
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'hint': 'No error message provided',
                'reasoning': 'Empty error message'
            }

        # First, check for HTTP status codes (enhanced categorization)
        status_code = self.extract_http_status_code(error_message)
        if status_code:
            if status_code == '401':
                return {
                    'category': 'authentication_failure',
                    'confidence': 0.95,
                    'hint': 'Check user credentials and authentication tokens. Verify login process and session management.',
                    'reasoning': f'HTTP 401 Unauthorized detected',
                    'status_code': status_code}
            elif status_code == '403':
                return {
                    'category': 'authorization_failure',
                    'confidence': 0.95,
                    'hint': 'Verify user permissions and access roles. Check authorization policies and user groups.',
                    'reasoning': f'HTTP 403 Forbidden detected',
                    'status_code': status_code
                }
            elif status_code == '404':
                return {
                    'category': 'resource_not_found',
                    'confidence': 0.90,
                    'hint': 'Verify URL paths and resource availability. Check routing and endpoint configurations.',
                    'reasoning': f'HTTP 404 Not Found detected',
                    'status_code': status_code
                }
            elif status_code in ['500', '502', '503', '504']:
                return {
                    'category': 'server_error',
                    'confidence': 0.90,
                    'hint': 'Check server logs and infrastructure health. Verify service dependencies and deployments.',
                    'reasoning': f'HTTP {status_code} server error detected',
                    'status_code': status_code
                }

        # Fall back to original comprehensive pattern matching
        for category, category_data in self.failure_patterns.items():
            for pattern in category_data['patterns']:
                if re.search(pattern, error_message, re.IGNORECASE):
                    confidence = category_data['confidence']
                    return {
                        'category': category,
                        'confidence': confidence,
                        'hint': category_data['hints'][0],  # Primary hint
                        'reasoning': f"Matched pattern: {pattern}",
                        'all_hints': category_data['hints']
                    }

        # No patterns matched
        return {
            'category': 'unknown',
            'confidence': 0.0,
            'hint': 'Manual investigation needed - pattern not recognized',
            'reasoning': 'No known failure patterns matched'
        }

    def map_environment(self, raw_env: str) -> str:
        """Map raw environment string to logical environment"""
        if not raw_env:
            return 'Unknown Environment'

        raw_env_lower = raw_env.lower().strip()
        return self.environment_mappings.get(raw_env_lower, f'Custom Environment ({raw_env})')

    def enhance_test_result(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a single test result with categorization and environment mapping"""
        enhanced = test_data.copy()

        # Map environment
        raw_env = test_data.get('environment', 'unknown')
        enhanced['environment'] = self.map_environment(raw_env)

        # Categorize failure if test failed
        if test_data.get('status') == 'FAIL' and test_data.get('error_message'):
            failure_analysis = self.categorize_failure(test_data['error_message'])
            enhanced['failure_category'] = failure_analysis['category']
            enhanced['failure_confidence'] = failure_analysis['confidence']
            enhanced['failure_hint'] = failure_analysis['hint']
            enhanced['failure_reasoning'] = failure_analysis['reasoning']

            # Include HTTP status code if detected
            if 'status_code' in failure_analysis:
                enhanced['http_status_code'] = failure_analysis['status_code']

        return enhanced

    def analyze_batch_results(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a batch of test results with enhanced categorization"""
        if not test_results:
            return {'message': 'No test results to analyze'}

        # Enhanced analysis with categorization
        failed_tests = [test for test in test_results if test.get('status') == 'FAIL']
        passed_tests = [test for test in test_results if test.get('status') == 'PASS']

        # Environment distribution
        env_distribution = {}
        failure_categories = {}

        enhanced_results = []
        for test in test_results:
            enhanced = self.enhance_test_result(test)
            enhanced_results.append(enhanced)

            # Track environment distribution
            env = enhanced['environment']
            env_distribution[env] = env_distribution.get(env, 0) + 1

            # Track failure categories
            if enhanced.get('failure_category'):
                category = enhanced['failure_category']
                failure_categories[category] = failure_categories.get(category, 0) + 1

        # Calculate statistics
        total_tests = len(test_results)
        pass_rate = (len(passed_tests) / total_tests) * 100 if total_tests > 0 else 0

        return {
            'summary': {
                'total_tests': total_tests,
                'passed': len(passed_tests),
                'failed': len(failed_tests),
                'pass_rate': round(pass_rate, 2)
            },
            'environment_distribution': env_distribution,
            'failure_categories': failure_categories,
            'enhanced_results': enhanced_results,
            'timestamp': datetime.now().isoformat()
        }

    def generate_failure_report(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed failure analysis report"""
        analysis = self.analyze_batch_results(test_results)

        if not analysis.get('failure_categories'):
            return {'message': 'No failures to analyze'}

        # Detailed failure breakdown
        failure_details = []
        for test in analysis['enhanced_results']:
            if test.get('failure_category'):
                failure_details.append({
                    'test_name': test.get('test_name', 'Unknown'),
                    'category': test['failure_category'],
                    'confidence': test.get('failure_confidence', 0),
                    'hint': test.get('failure_hint', ''),
                    'environment': test.get('environment', 'Unknown'),
                    'error_message': test.get('error_message', ''),
                    'http_status_code': test.get('http_status_code')
                })

        # Priority recommendations
        recommendations = []
        categories = analysis['failure_categories']

        # High priority: Authentication/Authorization failures
        auth_failures = categories.get('authentication_failure', 0) + categories.get('authorization_failure', 0)
        if auth_failures > 0:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Authentication/Authorization',
                'count': auth_failures,
                'action': 'Review user management and access control systems'
            })

        # Medium priority: Performance and connectivity
        perf_issues = categories.get('performance_issue', 0) + categories.get('connectivity_issue', 0)
        if perf_issues > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Performance/Connectivity',
                'count': perf_issues,
                'action': 'Optimize infrastructure and network configurations'
            })

        return {
            'failure_summary': analysis['failure_categories'],
            'failure_details': failure_details,
            'recommendations': recommendations,
            'total_failures': len(failure_details),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Simple demonstration
    print("🚀 Enhanced Local Analyzer - Demonstration")
    print("=" * 50)

    # Create analyzer instance
    analyzer = EnhancedLocalAnalyzer()

    # Demo failure categorization
    demo_errors = [
        "HTTP 401 Unauthorized: Invalid credentials",
        "HTTP 403 Forbidden: Access denied",
        "ElementNotInteractableException: Element not visible",
        "TimeoutException: Page load timeout",
        "ConnectionError: Host unreachable"
    ]

    for error in demo_errors:
        result = analyzer.categorize_failure(error)
        print(f"Error: {error}")
        print(f"  → Category: {result['category']} ({result['confidence']:.0%})")
        print(f"  → Hint: {result['hint']}")
        print()
