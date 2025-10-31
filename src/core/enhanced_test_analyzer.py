"""
Enhanced Test Log Analyzer - Improved categorization and environment mapping
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from test_log_analyzer import TestLogExtractor, FailureCategory, Priority

class EnhancedTestLogExtractor(TestLogExtractor):
    """Enhanced version with better categorization and environment mapping"""
    
    def __init__(self, json_file_path: str):
        super().__init__(json_file_path)
        self.environment_mapping = {
            # Common environment patterns
            'dev': ['dev', 'development', 'develop'],
            'qa': ['qa', 'test', 'testing', 'tst'],
            'staging': ['staging', 'stage', 'stg', 'uat', 'preprod'],
            'production': ['prod', 'production', 'live', 'prd']
        }
        
    def enhanced_categorize_failure(self) -> tuple[FailureCategory, Priority, str]:
        """Enhanced categorization with detailed reasoning"""
        if not self.test_data or self.test_data.get('status') != 'failed':
            return FailureCategory.UNKNOWN, Priority.LOW, "Test did not fail"
        
        failure_message = self.test_data.get('statusMessage', '').lower()
        status_trace = self.test_data.get('statusTrace', '').lower()
        test_name = self.test_data.get('name', '').lower()
        
        # Check for flaky test indicators
        is_flaky = self.test_data.get('retriesCount', 0) > 0 or self.test_data.get('flaky', False)
        
        # Enhanced categorization with detailed patterns
        
        # 1. Authentication/Authorization errors
        auth_patterns = [
            'unauthorized', 'forbidden', 'authentication', 'login', 'credentials',
            'access denied', 'permission denied', 'invalid token', 'session expired',
            'oauth', 'sso', 'saml'
        ]
        if any(pattern in failure_message for pattern in auth_patterns):
            return FailureCategory.AUTHENTICATION_ERROR, Priority.HIGH, "Authentication/authorization failure detected"
        
        # 2. Timeout errors with specific categorization
        timeout_patterns = ['timeout', 'timed out', 'waiting for', 'exceeded wait time']
        if any(pattern in failure_message for pattern in timeout_patterns) or 'timeout' in status_trace:
            if 'page load' in failure_message or 'navigation' in failure_message:
                return FailureCategory.TIMEOUT, Priority.HIGH, "Page load timeout - performance issue"
            elif 'element' in failure_message:
                return FailureCategory.TIMEOUT, Priority.MEDIUM, "Element wait timeout - possible UI change"
            else:
                priority = Priority.MEDIUM if is_flaky else Priority.HIGH
                return FailureCategory.TIMEOUT, priority, "General timeout - investigate performance"
        
        # 3. Element not found errors with specificity
        element_patterns = ['element not found', 'selector', 'locator', 'not visible', 'not attached']
        if any(pattern in failure_message for pattern in element_patterns):
            if 'button' in failure_message or 'click' in failure_message:
                return FailureCategory.ELEMENT_NOT_FOUND, Priority.MEDIUM, "Button/clickable element issue - UI change likely"
            elif 'input' in failure_message or 'form' in failure_message:
                return FailureCategory.ELEMENT_NOT_FOUND, Priority.MEDIUM, "Form element issue - check form changes"
            else:
                return FailureCategory.ELEMENT_NOT_FOUND, Priority.MEDIUM, "Element locator issue - selectors may need update"
        
        # 4. Network/API errors with HTTP status categorization
        network_patterns = ['network', 'connection', 'fetch', 'api', 'http']
        http_errors = ['500', '502', '503', '504', '404', '403', '401']
        if any(pattern in failure_message for pattern in network_patterns) or any(error in failure_message for error in http_errors):
            if '404' in failure_message:
                return FailureCategory.NETWORK_ERROR, Priority.MEDIUM, "404 Not Found - endpoint may have changed"
            elif any(code in failure_message for code in ['500', '502', '503', '504']):
                return FailureCategory.NETWORK_ERROR, Priority.HIGH, "Server error - infrastructure issue"
            elif 'connection refused' in failure_message or 'network error' in failure_message:
                return FailureCategory.NETWORK_ERROR, Priority.HIGH, "Network connectivity issue"
            else:
                return FailureCategory.NETWORK_ERROR, Priority.MEDIUM, "API/network communication issue"
        
        # 5. Data/State issues with specificity
        data_patterns = ['submit failed', 'pending', 'status', 'state', 'data']
        if any(pattern in failure_message for pattern in data_patterns):
            if 'submit failed' in failure_message:
                return FailureCategory.DATA_ISSUE, Priority.HIGH, "Form submission failure - data validation issue"
            elif 'pending' in failure_message:
                return FailureCategory.DATA_ISSUE, Priority.MEDIUM, "Pending state issue - async operation problem"
            else:
                return FailureCategory.DATA_ISSUE, Priority.MEDIUM, "Data state inconsistency"
        
        # 6. Assertion failures with context
        assertion_patterns = ['expect(', 'assertion', 'tocontain', 'tobe', 'tohave']
        if any(pattern in failure_message.replace(' ', '') for pattern in assertion_patterns):
            if 'text' in failure_message or 'content' in failure_message:
                return FailureCategory.ASSERTION_FAILURE, Priority.MEDIUM, "Text/content assertion failed - verify expected content"
            elif 'url' in failure_message or 'navigation' in failure_message:
                return FailureCategory.ASSERTION_FAILURE, Priority.MEDIUM, "URL/navigation assertion failed"
            else:
                return FailureCategory.ASSERTION_FAILURE, Priority.MEDIUM, "General assertion failure - verify test expectations"
        
        # 7. Browser/Infrastructure errors
        browser_patterns = ['browser', 'page crash', 'navigation', 'protocol', 'websocket', 'chrome', 'firefox']
        if any(pattern in failure_message for pattern in browser_patterns):
            return FailureCategory.BROWSER_ERROR, Priority.MEDIUM, "Browser/infrastructure issue - may be environmental"
        
        # 8. Environment issues
        env_patterns = ['environment', 'configuration', 'permission', 'access', 'policy']
        if any(pattern in failure_message for pattern in env_patterns):
            return FailureCategory.ENVIRONMENT_ISSUE, Priority.LOW, "Environment configuration issue"
        
        # 9. Enhanced flaky test detection
        if is_flaky:
            return FailureCategory.FLAKY_TEST, Priority.LOW, f"Flaky test detected ({self.test_data.get('retriesCount', 0)} retries)"
        
        # 10. Enhanced unknown categorization with analysis
        return self._analyze_unknown_failure(failure_message, status_trace)
    
    def _analyze_unknown_failure(self, failure_message: str, status_trace: str) -> tuple[FailureCategory, Priority, str]:
        """Analyze unknown failures to provide better insights"""
        analysis_hints = []
        
        # Look for specific error patterns
        if 'error:' in failure_message:
            error_part = failure_message.split('error:')[1].strip()[:50]
            analysis_hints.append(f"Error: {error_part}")
        
        # Check for JavaScript errors
        if any(js_error in failure_message for js_error in ['javascript', 'js', 'script', 'function']):
            analysis_hints.append("Possible JavaScript error")
        
        # Check for memory/performance issues
        if any(perf_issue in failure_message for perf_issue in ['memory', 'heap', 'slow', 'performance']):
            analysis_hints.append("Possible performance/memory issue")
        
        # Check for database/backend issues
        if any(db_issue in failure_message for db_issue in ['database', 'sql', 'connection pool', 'backend']):
            analysis_hints.append("Possible backend/database issue")
        
        # Check for third-party service issues
        if any(service in failure_message for service in ['service', 'external', 'third-party', 'integration']):
            analysis_hints.append("Possible third-party service issue")
        
        reason = "Unknown failure"
        if analysis_hints:
            reason = f"Unknown failure - {', '.join(analysis_hints)}"
        
        # Assign priority based on error characteristics
        priority = Priority.HIGH if any(critical in failure_message for critical in ['fatal', 'critical', 'severe']) else Priority.MEDIUM
        
        return FailureCategory.UNKNOWN, priority, reason
    
    def map_environment(self, raw_environment: str) -> str:
        """Map raw environment names to standard environment types"""
        if not raw_environment:
            return 'unknown'
        
        raw_env_lower = raw_environment.lower()
        
        # Direct environment mapping
        for env_type, patterns in self.environment_mapping.items():
            if any(pattern in raw_env_lower for pattern in patterns):
                return env_type
        
        # Pattern-based mapping for common formats
        # Example: linuxaa8d0014O1 -> extract meaningful parts
        
        # Look for environment indicators in the hostname/identifier
        if re.search(r'dev|development', raw_env_lower):
            return 'dev'
        elif re.search(r'qa|test|tst', raw_env_lower):
            return 'qa'
        elif re.search(r'stg|staging|uat|preprod', raw_env_lower):
            return 'staging'
        elif re.search(r'prod|production|live|prd', raw_env_lower):
            return 'production'
        
        # If no pattern matches, try to extract from hostname patterns
        # This can be customized based on your naming conventions
        return f'unclassified_{raw_environment[:10]}'  # Keep first 10 chars for reference
    
    def extract_performance_metrics(self) -> Dict[str, Any]:
        """Extract detailed performance metrics from test data"""
        metrics = {
            'duration_ms': 0,
            'duration_seconds': 0.0,
            'start_time': None,
            'end_time': None,
            'steps_count': 0,
            'slowest_step': None,
            'performance_category': 'normal'
        }
        
        if not self.test_data:
            return metrics
        
        # Extract basic duration
        duration_ms = self.test_data.get('duration', 0)
        metrics['duration_ms'] = duration_ms
        metrics['duration_seconds'] = duration_ms / 1000.0
        
        # Extract timestamps
        metrics['start_time'] = self.test_data.get('startTime')
        metrics['end_time'] = self.test_data.get('endTime')
        
        # Analyze steps if available
        steps = self.test_data.get('steps', [])
        metrics['steps_count'] = len(steps)
        
        if steps:
            # Find slowest step
            slowest_step = max(steps, key=lambda x: x.get('duration', 0), default={})
            if slowest_step:
                metrics['slowest_step'] = {
                    'title': slowest_step.get('title', 'Unknown'),
                    'duration_ms': slowest_step.get('duration', 0),
                    'duration_seconds': slowest_step.get('duration', 0) / 1000.0
                }
        
        # Categorize performance
        if duration_ms < 5000:  # < 5 seconds
            metrics['performance_category'] = 'fast'
        elif duration_ms < 30000:  # < 30 seconds
            metrics['performance_category'] = 'normal'
        elif duration_ms < 60000:  # < 1 minute
            metrics['performance_category'] = 'slow'
        else:  # > 1 minute
            metrics['performance_category'] = 'very_slow'
        
        return metrics
    
    def enhanced_extract_basic_info(self) -> Dict[str, Any]:
        """Enhanced extraction with all new features"""
        basic_info = super().extract_basic_info()
        
        # Add enhanced categorization
        category, priority, reason = self.enhanced_categorize_failure()
        
        # Add mapped environment
        raw_env = self.extract_environment_info()
        mapped_env = self.map_environment(raw_env)
        
        # Add performance metrics
        perf_metrics = self.extract_performance_metrics()
        
        # Convert to dict and enhance
        enhanced_info = {
            'test_name': basic_info.test_name,
            'full_name': basic_info.full_name,
            'status': basic_info.status,
            'duration_ms': perf_metrics['duration_ms'],
            'duration_seconds': perf_metrics['duration_seconds'],
            'failure_reason': reason,  # Enhanced reason
            'error_location': basic_info.error_location,
            'retries_count': basic_info.retries_count,
            'test_file': basic_info.test_file,
            'tags': basic_info.tags,
            'failure_category': category.value if category else 'Unknown',
            'priority': priority.value if priority else 'Medium',
            'is_flaky': basic_info.is_flaky,
            'raw_environment': raw_env,
            'environment': mapped_env,  # New mapped environment
            'needs_attention': basic_info.status == 'failed',
            'performance_metrics': perf_metrics,  # New performance data
            'analysis_timestamp': self.test_data.get('timestamp') if self.test_data else None
        }
        
        return enhanced_info