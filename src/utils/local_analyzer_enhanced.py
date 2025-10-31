#!/usr/bin/env python3
"""
Local Test Log Analyzer - Enhanced Version with Built-in Enhancements
Analyzes test logs from local directories with enhanced categorization, environment mapping, and performance analytics
"""

import os
import sys
import json
import argparse
import logging
import re
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our existing modules
try:
    # Try relative imports first (when run as module)
    from ..core.test_log_analyzer import TestLogExtractor, BatchTestAnalyzer
    from ..core.automated_scheduler import TestAnalysisScheduler
except ImportError:
    try:
        # Fallback to absolute imports (when run directly)
        import sys
        import os
        # Add the src directory to path
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        src_dir = os.path.dirname(current_dir)  # Go up from utils to src
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        from core.test_log_analyzer import TestLogExtractor, BatchTestAnalyzer
        from core.automated_scheduler import TestAnalysisScheduler
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("💡 Make sure you're in the correct directory and have run the setup script")
        print("💡 Try running: .\\scripts\\setup.ps1")
        sys.exit(1)

# Built-in Enhanced Analysis Components
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

class AdvancedMetricsAnalyzer:
    """Provides advanced metrics and business insights for test analysis"""
    
    def __init__(self):
        # Business feature patterns
        self.feature_patterns = {
            'account_establishment': r'account.*establishment',
            'dao_features': r'dao.*',
            'legacy_features': r'legacy.*',
            'beneficiary_management': r'beneficiary.*',
            'proposal_handling': r'proposal.*',
            'referrer_system': r'referrer.*',
            'relationship_management': r'relationship.*'
        }
        
        # Critical business flows
        self.critical_flows = {
            'user_onboarding': ['account.*establishment', 'referrer.*information'],
            'beneficiary_setup': ['beneficiary.*act', 'relationship.*type'],
            'proposal_process': ['proposal.*solution', 'proposal.*details']
        }
    
    def analyze_business_impact(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze business impact and feature area breakdown"""
        
        feature_breakdown = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0})
        critical_flow_health = {}
        
        # Analyze by feature area
        for test in test_results:
            test_name = test.get('test_name', '').lower()
            status = test.get('status', 'unknown')
            
            # Categorize by feature
            categorized = False
            for feature, pattern in self.feature_patterns.items():
                if re.search(pattern, test_name):
                    feature_breakdown[feature]['total'] += 1
                    if status == 'passed':
                        feature_breakdown[feature]['passed'] += 1
                    elif status == 'failed':
                        feature_breakdown[feature]['failed'] += 1
                    categorized = True
                    break
            
            if not categorized:
                feature_breakdown['other']['total'] += 1
                if status == 'passed':
                    feature_breakdown['other']['passed'] += 1
                elif status == 'failed':
                    feature_breakdown['other']['failed'] += 1
        
        # Calculate pass rates
        for feature, data in feature_breakdown.items():
            if data['total'] > 0:
                data['pass_rate'] = (data['passed'] / data['total']) * 100
        
        # Analyze critical business flows
        for flow_name, patterns in self.critical_flows.items():
            flow_tests = []
            for test in test_results:
                test_name = test.get('test_name', '').lower()
                for pattern in patterns:
                    if re.search(pattern, test_name):
                        flow_tests.append(test)
                        break
            
            if flow_tests:
                total_flow_tests = len(flow_tests)
                passed_flow_tests = sum(1 for t in flow_tests if t.get('status') == 'passed')
                health_score = (passed_flow_tests / total_flow_tests * 100) if total_flow_tests > 0 else 0
                critical_flow_health[flow_name] = {
                    'total_tests': total_flow_tests,
                    'passed_tests': passed_flow_tests,
                    'health_score': health_score,
                    'risk_level': self._calculate_risk_level(health_score)
                }
        
        return {
            'feature_breakdown': dict(feature_breakdown),
            'critical_flow_health': critical_flow_health,
            'business_insights': self._generate_business_insights(feature_breakdown, critical_flow_health)
        }
    
    def analyze_failure_patterns(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze failure patterns and provide actionable insights"""
        
        failed_tests = [t for t in test_results if t.get('status') == 'failed']
        if not failed_tests:
            return {'message': 'No failed tests to analyze'}
        
        # Pattern analysis
        failure_patterns = {
            'common_error_keywords': Counter(),
            'element_interaction_issues': [],
            'timing_related_failures': [],
            'data_validation_failures': []
        }
        
        for test in failed_tests:
            failure_reason = test.get('failure_reason', '').lower()
            test_name = test.get('test_name', '')
            
            if failure_reason:
                # Extract keywords from failure reasons
                words = re.findall(r'\b\w+\b', failure_reason)
                significant_words = [w for w in words if len(w) > 3 and w not in ['test', 'should', 'have', 'when', 'with', 'this', 'that']]
                failure_patterns['common_error_keywords'].update(significant_words)
                
                # Categorize specific failure types
                if any(keyword in failure_reason for keyword in ['element', 'selector', 'locator', 'click', 'visible']):
                    failure_patterns['element_interaction_issues'].append({
                        'test_name': test_name,
                        'issue': 'Element interaction failure',
                        'suggestion': 'Review page object model and element selectors'
                    })
        
        # Get top error keywords
        top_keywords = failure_patterns['common_error_keywords'].most_common(10)
        
        return {
            'total_failed_tests': len(failed_tests),
            'top_error_keywords': top_keywords,
            'element_interaction_issues': failure_patterns['element_interaction_issues'][:5],
            'failure_insights': self._generate_failure_insights(failure_patterns, top_keywords)
        }
    
    def _calculate_risk_level(self, health_score: float) -> str:
        """Calculate risk level based on health score"""
        if health_score >= 95:
            return 'Low'
        elif health_score >= 80:
            return 'Medium'
        elif health_score >= 60:
            return 'High'
        else:
            return 'Critical'
    
    def _generate_business_insights(self, feature_breakdown: Dict, critical_flow_health: Dict) -> List[str]:
        """Generate business-focused insights"""
        insights = []
        
        # Feature area insights
        for feature, data in feature_breakdown.items():
            if data['total'] > 0 and data['pass_rate'] < 80:
                insights.append(f"{feature.replace('_', ' ').title()} area has {data['pass_rate']:.1f}% pass rate - needs attention")
        
        # Critical flow insights
        for flow, health in critical_flow_health.items():
            if health['risk_level'] in ['High', 'Critical']:
                insights.append(f"{flow.replace('_', ' ').title()} flow is at {health['risk_level'].lower()} risk with {health['health_score']:.1f}% health")
        
        return insights
    
    def _generate_failure_insights(self, failure_patterns: Dict, top_keywords: List) -> List[str]:
        """Generate failure-specific insights"""
        insights = []
        
        if top_keywords:
            top_keyword = top_keywords[0][0]
            insights.append(f"Most common failure keyword: '{top_keyword}' - focus debugging efforts here")
        
        element_issues = len(failure_patterns['element_interaction_issues'])
        if element_issues > 0:
            insights.append(f"{element_issues} tests failing on element interactions - UI changes may have occurred")
        
        return insights

class EnhancedAnalyzer:
    """Built-in enhanced analysis to avoid import issues"""
    
    def __init__(self):
        # Environment mapping patterns
        self.environment_mapping = {
            r'dev.*linux.*': 'dev',
            r'qa.*server.*': 'qa', 
            r'staging.*': 'staging',
            r'prod.*': 'production',
            r'.*unittest.*': 'dev',
            r'.*performance.*': 'staging',
            r'.*test.*': 'qa',
            r'.*development.*': 'dev'
        }
        
        # Enhanced failure categorization patterns
        self.failure_patterns = {
            'authentication_failure': {
                'patterns': [
                    r'authentication.*failed',
                    r'invalid.*credentials',
                    r'login.*failed',
                    r'unauthorized',
                    r'401.*error',
                    r'auth.*error'
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
                    r'performance.*threshold.*exceeded',
                    r'timed.*out',
                    r'timeout.*error'
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
                    r'http.*error.*[45]\d{2}',
                    r'fetch.*failed'
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
                    r'element.*not.*visible',
                    r'no.*such.*element'
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
                    r'data.*validation.*failed',
                    r'assert.*error'
                ],
                'hints': [
                    "Review test data setup and ensure correct values",
                    "Check for data dependencies and prerequisites",
                    "Verify database state and test data isolation"
                ]
            },
            'browser_infrastructure': {
                'patterns': [
                    r'browser.*crashed',
                    r'driver.*error',
                    r'selenium.*error',
                    r'webdriver.*exception',
                    r'browser.*not.*responding'
                ],
                'hints': [
                    "Check browser and WebDriver compatibility",
                    "Verify infrastructure stability and resources",
                    "Review browser configuration and settings"
                ]
            },
            'environment_issue': {
                'patterns': [
                    r'environment.*error',
                    r'service.*unavailable',
                    r'database.*connection.*failed',
                    r'server.*error.*5\d{2}'
                ],
                'hints': [
                    "Check environment availability and service status",
                    "Verify database connectivity and configuration",
                    "Review infrastructure health and dependencies"
                ]
            }
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'fast': 5000,      # < 5 seconds
            'normal': 30000,   # < 30 seconds  
            'slow': 60000,     # < 1 minute
            'very_slow': float('inf')  # >= 1 minute
        }
    
    def map_environment(self, raw_environment: str) -> str:
        """Map raw environment string to logical environment"""
        if not raw_environment:
            return 'unknown'
        
        raw_env_lower = raw_environment.lower()
        
        for pattern, mapped_env in self.environment_mapping.items():
            if re.search(pattern, raw_env_lower):
                return mapped_env
        
        return 'unknown'
    
    def categorize_failure(self, failure_reason: str) -> Dict[str, Any]:
        """Enhanced failure categorization with specific hints"""
        if not failure_reason:
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'hint': 'No failure reason provided',
                'reasoning': 'Cannot categorize without failure details'
            }
        
        failure_lower = failure_reason.lower()
        
        for category, category_data in self.failure_patterns.items():
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
    
    def enhance_test_result(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a single test result with categorization and environment mapping"""
        enhanced = test_data.copy()
        
        # Map environment
        raw_env = test_data.get('environment', 'unknown')
        enhanced['environment'] = self.map_environment(raw_env)
        enhanced['environment_source'] = raw_env
        
        # Enhanced categorization for failed tests
        if test_data.get('status') == 'failed':
            failure_reason = test_data.get('failure_reason', '')
            categorization = self.categorize_failure(failure_reason)
            
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
    
    def analyze_performance(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test performance metrics"""
        
        if not test_results:
            return {'error': 'No test results provided'}
        
        # Extract durations
        durations = []
        for test in test_results:
            duration_ms = test.get('duration_ms', 0)
            if duration_ms == 0:
                # Try alternative duration fields
                duration_ms = test.get('duration', 0)
                if isinstance(duration_ms, (int, float)) and duration_ms < 1000:
                    duration_ms = duration_ms * 1000  # Convert seconds to ms
            
            if duration_ms > 0:
                durations.append(duration_ms)
        
        if not durations:
            return {'error': 'No valid duration data found'}
        
        # Calculate statistics
        analysis = {
            'total_tests_analyzed': len(durations),
            'total_execution_time_ms': sum(durations),
            'total_execution_time_minutes': sum(durations) / 60000,
            'average_duration_ms': statistics.mean(durations),
            'average_duration_seconds': statistics.mean(durations) / 1000,
            'median_duration_ms': statistics.median(durations),
            'median_duration_seconds': statistics.median(durations) / 1000,
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
        }
        
        # Performance distribution
        distribution = {'fast': 0, 'normal': 0, 'slow': 0, 'very_slow': 0}
        for duration in durations:
            if duration < self.performance_thresholds['fast']:
                distribution['fast'] += 1
            elif duration < self.performance_thresholds['normal']:
                distribution['normal'] += 1
            elif duration < self.performance_thresholds['slow']:
                distribution['slow'] += 1
            else:
                distribution['very_slow'] += 1
        
        analysis['performance_distribution'] = distribution
        analysis['performance_percentages'] = {
            category: (count / len(durations) * 100) 
            for category, count in distribution.items()
        }
        
        return analysis

class LocalTestAnalyzer:
    """Enhanced local test log analyzer with built-in enhanced features"""
    
    def __init__(self, input_dir, output_dir=None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else Path("./output/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize batch analyzer with input directory
        self.batch_analyzer = BatchTestAnalyzer(str(self.input_dir))
        
        # Initialize built-in enhanced analyzer
        self.enhanced_analyzer = EnhancedAnalyzer()
        
        # Initialize advanced metrics analyzer
        self.advanced_metrics = AdvancedMetricsAnalyzer()
        
        # Try to initialize scheduler for notification capabilities (optional)
        try:
            self.scheduler = TestAnalysisScheduler()
        except Exception:
            self.scheduler = None  # Optional if not available
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def find_test_files(self, pattern="*.json"):
        """Find all test log files in the input directory"""
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")
        
        files = list(self.input_dir.glob(pattern))
        if not files:
            # Try common patterns
            patterns = ["*.json", "**/*.json", "*result*.json", "*test*.json"]
            for p in patterns:
                files = list(self.input_dir.glob(p))
                if files:
                    break
        
        self.logger.info(f"Found {len(files)} test files in {self.input_dir}")
        return files
    
    def analyze_local_files(self, send_notifications=False, generate_reports=True, use_enhanced=True):
        """
        Analyze local test files with enhanced categorization, environment mapping, and performance analytics
        
        Args:
            send_notifications: Whether to send notifications (requires .env setup)
            generate_reports: Whether to generate detailed reports
            use_enhanced: Whether to use enhanced analysis features
        """
        try:
            print(f"🔍 Analyzing test logs from: {self.input_dir}")
            print(f"📊 Output directory: {self.output_dir}")
            
            # Find test files
            test_files = self.find_test_files()
            if not test_files:
                print(f"❌ No test files found in {self.input_dir}")
                print("💡 Supported formats: JSON files from Playwright test execution")
                return None
            
            # Analyze files with basic extraction
            print(f"📋 Processing {len(test_files)} files...")
            results = []
            
            for file_path in test_files:
                try:
                    # Create extractor for each file
                    extractor = TestLogExtractor(str(file_path))
                    result = extractor.extract_basic_info()
                    if result:
                        # Convert dataclass to dict for compatibility
                        result_dict = {
                            'test_name': result.test_name,
                            'full_name': result.full_name,
                            'status': result.status,
                            'duration_ms': result.duration_ms,
                            'duration_seconds': result.duration_seconds,
                            'failure_reason': result.failure_reason,
                            'error_location': result.error_location,
                            'retries_count': result.retries_count,
                            'test_file': result.test_file,
                            'tags': result.tags,
                            'failure_category': result.failure_category,
                            'priority': result.priority,
                            'is_flaky': result.is_flaky,
                            'environment': result.environment,
                            'source_file': file_path.name
                        }
                        results.append(result_dict)
                        print(f"✅ Analyzed: {file_path.name}")
                except Exception as e:
                    print(f"⚠️  Skipped {file_path.name}: {e}")
            
            if not results:
                print("❌ No valid test results found")
                return None
            
            if use_enhanced:
                print(f"\n🚀 Applying enhanced analysis to {len(results)} test results...")
                
                # Apply enhanced analysis
                enhanced_results = []
                unknown_before = 0
                unknown_after = 0
                
                for test in results:
                    # Track improvement in categorization
                    original_category = test.get('failure_category', 'unknown')
                    if original_category.lower() in ['unknown', 'other', 'n/a'] and test.get('status') == 'failed':
                        unknown_before += 1
                    
                    # Enhance the test result
                    enhanced_test = self.enhanced_analyzer.enhance_test_result(test)
                    enhanced_results.append(enhanced_test)
                    
                    # Track after enhancement
                    new_category = enhanced_test.get('failure_category', 'unknown')
                    if new_category.lower() in ['unknown', 'other', 'n/a'] and test.get('status') == 'failed':
                        unknown_after += 1
                
                # Perform performance analysis
                performance_analysis = self.enhanced_analyzer.analyze_performance(enhanced_results)
                
                # Perform advanced metrics analysis
                print("🔬 Analyzing business impact and failure patterns...")
                business_analysis = self.advanced_metrics.analyze_business_impact(enhanced_results)
                failure_analysis = self.advanced_metrics.analyze_failure_patterns(enhanced_results)
                
                # Calculate improvements
                improvements = {
                    'unknown_before': unknown_before,
                    'unknown_after': unknown_after,
                    'improvement_count': unknown_before - unknown_after,
                    'improvement_percentage': ((unknown_before - unknown_after) / len(results) * 100) if results else 0
                }
                
                # Display enhanced summary
                self.display_enhanced_summary(enhanced_results, performance_analysis, improvements, business_analysis, failure_analysis)
                
                if generate_reports:
                    # Generate enhanced reports
                    report_files = self.generate_enhanced_reports(enhanced_results, performance_analysis, improvements, business_analysis, failure_analysis)
                    print(f"\n📊 Enhanced reports generated:")
                    for report_file in report_files:
                        print(f"   - {report_file}")
                
                return {
                    'enhanced_results': enhanced_results,
                    'performance_analysis': performance_analysis,
                    'business_analysis': business_analysis,
                    'failure_analysis': failure_analysis,
                    'improvements': improvements,
                    'total_tests': len(enhanced_results)
                }
            else:
                # Fall back to basic analysis
                analysis = self.generate_basic_analysis(results)
                self.display_basic_summary(analysis)
                return analysis
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            print(f"❌ Analysis failed: {e}")
            return None
    
    def display_enhanced_summary(self, enhanced_results: List[Dict[str, Any]], 
                                performance_analysis: Dict[str, Any], improvements: Dict[str, Any],
                                business_analysis: Dict[str, Any], failure_analysis: Dict[str, Any]):
        """Display enhanced analysis summary to console with all new features including advanced metrics"""
        print("\n" + "="*80)
        print("🚀 ENHANCED TEST ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"📁 Source Directory: {self.input_dir}")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Enhanced Features: Categorization + Environment + Performance + Business Impact")
        print()
        
        # Basic metrics
        total_tests = len(enhanced_results)
        passed_tests = sum(1 for test in enhanced_results if test.get('status') == 'passed')
        failed_tests = sum(1 for test in enhanced_results if test.get('status') == 'failed')
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 EXECUTION METRICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({pass_rate:.1f}%)")
        print(f"   Failed: {failed_tests} ({100-pass_rate:.1f}%)")
        print()
        
        # Show improvements made by enhanced analyzer
        if improvements.get('improvement_count', 0) > 0:
            print(f"✨ ENHANCED CATEGORIZATION IMPROVEMENTS:")
            print(f"   Unknown Categories Before: {improvements.get('unknown_before', 0)}")
            print(f"   Unknown Categories After: {improvements.get('unknown_after', 0)}")
            print(f"   Categories Resolved: {improvements.get('improvement_count', 0)}")
            print(f"   Improvement Rate: {improvements.get('improvement_percentage', 0):.1f}%")
            print()
        
        # Business Impact Analysis
        feature_breakdown = business_analysis.get('feature_breakdown', {})
        if feature_breakdown:
            print(f"🏢 BUSINESS FEATURE ANALYSIS:")
            for feature, data in sorted(feature_breakdown.items(), key=lambda x: x[1]['total'], reverse=True):
                if data['total'] > 0:
                    print(f"   - {feature.replace('_', ' ').title()}: {data['total']} tests ({data['pass_rate']:.1f}% pass rate)")
            print()
        
        # Critical Business Flow Health
        critical_flows = business_analysis.get('critical_flow_health', {})
        if critical_flows:
            print(f"🎯 CRITICAL BUSINESS FLOW HEALTH:")
            for flow_name, health in critical_flows.items():
                risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🟠', 'Critical': '🔴'}.get(health['risk_level'], '⚪')
                print(f"   {risk_emoji} {flow_name.replace('_', ' ').title()}: {health['health_score']:.1f}% ({health['risk_level']} Risk)")
            print()
        
        # Enhanced failure categories
        category_counts = {}
        environment_counts = {}
        failure_hints = []
        
        for test in enhanced_results:
            # Count categories
            category = test.get('failure_category', 'unknown')
            if test.get('status') == 'failed':
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count environments
            env = test.get('environment', 'unknown')
            environment_counts[env] = environment_counts.get(env, 0) + 1
            
            # Collect failure hints
            hint = test.get('failure_hint')
            if hint and test.get('status') == 'failed' and 'manual investigation' not in hint.lower():
                failure_hints.append({
                    'test_name': test.get('test_name', 'Unknown'),
                    'category': category,
                    'hint': hint,
                    'environment': env
                })
        
        if category_counts:
            print(f"🏷️ ENHANCED FAILURE CATEGORIES:")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / failed_tests) * 100 if failed_tests > 0 else 0
                category_display = category.replace('_', ' ').title()
                print(f"   - {category_display}: {count} tests ({percentage:.1f}%)")
            print()
        
        # Failure Pattern Analysis
        if failure_analysis.get('top_error_keywords'):
            print(f"🔍 FAILURE PATTERN ANALYSIS:")
            top_keywords = failure_analysis.get('top_error_keywords', [])[:5]
            print(f"   Top Error Keywords: {', '.join([f'{word}({count})' for word, count in top_keywords])}")
            
            element_issues = len(failure_analysis.get('element_interaction_issues', []))
            if element_issues > 0:
                print(f"   Element Interaction Issues: {element_issues} tests")
            
            failure_insights = failure_analysis.get('failure_insights', [])
            if failure_insights:
                print(f"   Key Insight: {failure_insights[0]}")
            print()
        
        # Environment analysis
        if environment_counts:
            print(f"🌍 ENVIRONMENT ANALYSIS:")
            for env, count in sorted(environment_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_tests) * 100
                print(f"   - {env.capitalize()}: {count} tests ({percentage:.1f}%)")
            print()
        
        # Performance insights
        if performance_analysis and 'error' not in performance_analysis:
            print(f"⚡ PERFORMANCE INSIGHTS:")
            print(f"   Average Duration: {performance_analysis.get('average_duration_seconds', 0):.1f} seconds")
            print(f"   Total Execution Time: {performance_analysis.get('total_execution_time_minutes', 0):.1f} minutes")
            
            perf_dist = performance_analysis.get('performance_percentages', {})
            print(f"   Fast Tests (<5s): {perf_dist.get('fast', 0):.1f}%")
            print(f"   Normal Tests (5-30s): {perf_dist.get('normal', 0):.1f}%")
            print(f"   Slow Tests (>30s): {perf_dist.get('slow', 0) + perf_dist.get('very_slow', 0):.1f}%")
            print()
        
        # Business Insights
        business_insights = business_analysis.get('business_insights', [])
        if business_insights:
            print(f"💼 BUSINESS INSIGHTS:")
            for insight in business_insights[:3]:
                print(f"   • {insight}")
            print()
        
        # Top actionable insights
        if failure_hints:
            print(f"💡 TOP ACTIONABLE INSIGHTS:")
            for i, hint_data in enumerate(failure_hints[:5], 1):
                print(f"   {i}. {hint_data['test_name']} ({hint_data['category']}):")
                print(f"      {hint_data['hint']}")
            print()
        
        print("="*80)
    
    def display_basic_summary(self, analysis):
        """Display basic analysis summary"""
        print("\n" + "="*60)
        print("📊 BASIC TEST ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📁 Source Directory: {self.input_dir}")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Basic metrics
        total_tests = analysis['total_tests']
        failed_tests = analysis['failed_tests']
        passed_tests = analysis['passed_tests']
        pass_rate = analysis['pass_rate']
        
        print(f"🎯 EXECUTION METRICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({pass_rate:.1f}%)")
        print(f"   Failed: {failed_tests} ({100-pass_rate:.1f}%)")
        print()
        
        print("="*60)
    
    def generate_enhanced_reports(self, enhanced_results: List[Dict[str, Any]], 
                                 performance_analysis: Dict[str, Any], improvements: Dict[str, Any],
                                 business_analysis: Dict[str, Any], failure_analysis: Dict[str, Any]):
        """Generate enhanced reports with all new features including advanced metrics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_files = []
        
        try:
            # Generate comprehensive enhanced report
            report_content = self.generate_enhanced_report_content(enhanced_results, performance_analysis, improvements, business_analysis, failure_analysis)
            comprehensive_file = self.output_dir / f"enhanced_report_{timestamp}.md"
            with open(comprehensive_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            report_files.append(str(comprehensive_file))
            
            # Generate business impact report
            business_report = self.generate_business_impact_report(business_analysis, failure_analysis, enhanced_results)
            business_file = self.output_dir / f"business_impact_report_{timestamp}.md"
            with open(business_file, 'w', encoding='utf-8') as f:
                f.write(business_report)
            report_files.append(str(business_file))
            
            # Generate CSV with enhanced data
            csv_file = self.output_dir / f"enhanced_tests_{timestamp}.csv"
            self.save_enhanced_csv(enhanced_results, str(csv_file))
            report_files.append(str(csv_file))
            
            # Generate JSON export
            json_file = self.output_dir / f"enhanced_analysis_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'enhanced_results': enhanced_results,
                    'performance_analysis': performance_analysis,
                    'business_analysis': business_analysis,
                    'failure_analysis': failure_analysis,
                    'improvements': improvements,
                    'metadata': {
                        'analysis_timestamp': datetime.now().isoformat(),
                        'total_tests': len(enhanced_results),
                        'analyzer_version': '2.1.0'
                    }
                }, f, indent=2, default=str)
            report_files.append(str(json_file))
            
        except Exception as e:
            self.logger.error(f"Enhanced report generation failed: {e}")
            print(f"⚠️  Enhanced report generation partially failed: {e}")
        
        return report_files
    
    def generate_enhanced_report_content(self, enhanced_results: List[Dict[str, Any]], 
                                       performance_analysis: Dict[str, Any], 
                                       improvements: Dict[str, Any],
                                       business_analysis: Dict[str, Any] = None,
                                       failure_analysis: Dict[str, Any] = None) -> str:
        """Generate comprehensive enhanced report content"""
        
        total_tests = len(enhanced_results)
        passed_tests = sum(1 for test in enhanced_results if test.get('status') == 'passed')
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = []
        report.append("# 🚀 Enhanced Test Analysis Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("## 📊 Executive Summary")
        report.append(f"- **Total Tests**: {total_tests}")
        report.append(f"- **Pass Rate**: {pass_rate:.1f}%")
        report.append(f"- **Failed Tests**: {failed_tests}")
        report.append("")
        
        # Improvements Made
        if improvements.get('improvement_count', 0) > 0:
            report.append("## 🎯 Analysis Improvements")
            report.append(f"- **Unknown Categories Resolved**: {improvements.get('improvement_count', 0)}")
            report.append(f"- **Categorization Improvement**: {improvements.get('improvement_percentage', 0):.1f}%")
            report.append(f"- **Remaining Unknown**: {improvements.get('unknown_after', 0)} tests")
            report.append("")
        
        # Enhanced Categorization
        category_counts = {}
        for test in enhanced_results:
            if test.get('status') == 'failed':
                category = test.get('failure_category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            report.append("## 🏷️ Enhanced Failure Categories")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / failed_tests * 100) if failed_tests > 0 else 0
                report.append(f"- **{category.replace('_', ' ').title()}**: {count} tests ({percentage:.1f}%)")
            report.append("")
        
        # Environment Analysis
        env_counts = {}
        for test in enhanced_results:
            env = test.get('environment', 'unknown')
            env_counts[env] = env_counts.get(env, 0) + 1
        
        if env_counts:
            report.append("## 🌍 Environment Analysis")
            for env, count in sorted(env_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_tests * 100)
                report.append(f"- **{env.capitalize()}**: {count} tests ({percentage:.1f}%)")
            report.append("")
        
        # Performance Analysis
        if performance_analysis and 'error' not in performance_analysis:
            report.append("## ⚡ Performance Insights")
            report.append(f"- **Average Duration**: {performance_analysis.get('average_duration_seconds', 0):.1f} seconds")
            report.append(f"- **Total Execution Time**: {performance_analysis.get('total_execution_time_minutes', 0):.1f} minutes")
            
            perf_dist = performance_analysis.get('performance_percentages', {})
            report.append(f"- **Fast Tests** (<5s): {perf_dist.get('fast', 0):.1f}%")
            report.append(f"- **Slow Tests** (>30s): {perf_dist.get('slow', 0) + perf_dist.get('very_slow', 0):.1f}%")
            report.append("")
        
        # Business Analysis Section
        if business_analysis:
            report.append("## 🏢 Business Impact Analysis")
            
            # Feature areas
            if 'feature_breakdown' in business_analysis:
                report.append("### Feature Area Health")
                for feature, data in business_analysis['feature_breakdown'].items():
                    health_status = "🟢" if data['pass_rate'] >= 80 else "🟠" if data['pass_rate'] >= 60 else "🔴"
                    report.append(f"- {health_status} **{feature}**: {data['pass_rate']:.1f}% ({data['passed']}/{data['total']} tests)")
                report.append("")
            
            # Critical flows
            if 'critical_flows' in business_analysis:
                report.append("### Critical Business Flow Health")
                for flow, health in business_analysis['critical_flows'].items():
                    status_icon = "🟢" if health >= 80 else "🟠" if health >= 60 else "🔴"
                    risk_level = "Low Risk" if health >= 80 else "High Risk" if health >= 60 else "Critical Risk"
                    report.append(f"- {status_icon} **{flow}**: {health:.1f}% ({risk_level})")
                report.append("")
        
        # Failure Pattern Analysis
        if failure_analysis:
            report.append("## 🔍 Failure Pattern Analysis")
            
            if 'top_keywords' in failure_analysis:
                keywords_str = ", ".join([f"{k}({v})" for k, v in failure_analysis['top_keywords'].items()])
                report.append(f"**Top Error Keywords**: {keywords_str}")
                report.append("")
            
            if 'patterns' in failure_analysis:
                report.append("**Key Patterns Identified**:")
                for pattern, count in failure_analysis['patterns'].items():
                    report.append(f"- {pattern}: {count} tests")
                report.append("")
        
        # Top Actionable Insights
        failure_hints = []
        for test in enhanced_results:
            hint = test.get('failure_hint')
            if hint and test.get('status') == 'failed' and 'manual investigation' not in hint.lower():
                failure_hints.append({
                    'test_name': test.get('test_name', 'Unknown'),
                    'category': test.get('failure_category', 'unknown'),
                    'hint': hint,
                    'environment': test.get('environment', 'unknown')
                })
        
        if failure_hints:
            report.append("## 💡 Top Actionable Insights")
            for i, hint_data in enumerate(failure_hints[:10], 1):
                report.append(f"{i}. **{hint_data['test_name']}** ({hint_data['category']}):")
                report.append(f"   {hint_data['hint']}")
                report.append(f"   *Environment: {hint_data['environment']}*")
                report.append("")
        
        return "\n".join(report)
    
    def generate_business_impact_report(self, business_analysis: Dict[str, Any], 
                                       failure_analysis: Dict[str, Any], enhanced_results: List[Dict[str, Any]]) -> str:
        """Generate a business-focused impact report"""
        
        total_tests = len(enhanced_results)
        failed_tests = sum(1 for test in enhanced_results if test.get('status') == 'failed')
        
        report = []
        report.append("# 💼 Business Impact Analysis Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary for Business
        report.append("## 📈 Executive Summary")
        report.append(f"- **Total Test Coverage**: {total_tests} tests across business features")
        report.append(f"- **Quality Gate Status**: {'✅ PASSED' if failed_tests < total_tests * 0.1 else '⚠️ ATTENTION NEEDED'}")
        report.append(f"- **Business Risk Level**: {self._assess_business_risk(business_analysis, failed_tests, total_tests)}")
        report.append("")
        
        # Feature Area Health
        feature_breakdown = business_analysis.get('feature_breakdown', {})
        if feature_breakdown:
            report.append("## 🏢 Feature Area Health Dashboard")
            
            # Sort by business criticality (based on test count and pass rate)
            sorted_features = sorted(feature_breakdown.items(), 
                                   key=lambda x: (x[1]['total'], x[1]['pass_rate']), reverse=True)
            
            for feature, data in sorted_features:
                if data['total'] > 0:
                    status_emoji = "🟢" if data['pass_rate'] >= 95 else "🟡" if data['pass_rate'] >= 80 else "🔴"
                    report.append(f"### {status_emoji} {feature.replace('_', ' ').title()}")
                    report.append(f"- **Test Coverage**: {data['total']} tests")
                    report.append(f"- **Success Rate**: {data['pass_rate']:.1f}%")
                    report.append(f"- **Failed Tests**: {data['failed']}")
                    if data['pass_rate'] < 80:
                        report.append(f"- **⚠️ Action Required**: Feature needs immediate attention")
                    report.append("")
        
        # Critical Business Flow Analysis
        critical_flows = business_analysis.get('critical_flow_health', {})
        if critical_flows:
            report.append("## 🎯 Critical Business Flow Status")
            for flow_name, health in critical_flows.items():
                risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🟠', 'Critical': '🔴'}.get(health['risk_level'], '⚪')
                report.append(f"### {risk_emoji} {flow_name.replace('_', ' ').title()}")
                report.append(f"- **Health Score**: {health['health_score']:.1f}%")
                report.append(f"- **Risk Level**: {health['risk_level']}")
                report.append(f"- **Test Coverage**: {health['total_tests']} tests")
                
                if health['risk_level'] in ['High', 'Critical']:
                    report.append(f"- **🚨 Business Impact**: Critical user journey at risk")
                    report.append(f"- **Recommended Action**: Immediate investigation and remediation")
                report.append("")
        
        # Failure Impact Analysis
        if failure_analysis.get('top_error_keywords'):
            report.append("## 🔍 Failure Impact Analysis")
            
            top_keywords = failure_analysis.get('top_error_keywords', [])[:5]
            report.append("### Most Common Issues:")
            for keyword, count in top_keywords:
                report.append(f"- **{keyword.title()}**: {count} occurrences")
            report.append("")
            
            element_issues = len(failure_analysis.get('element_interaction_issues', []))
            if element_issues > 0:
                report.append(f"### UI/UX Impact:")
                report.append(f"- **{element_issues} tests** failing due to element interaction issues")
                report.append(f"- **Likely Cause**: Recent UI changes or page structure modifications")
                report.append(f"- **Business Impact**: User interface functionality may be compromised")
                report.append("")
        
        # Business Recommendations
        business_insights = business_analysis.get('business_insights', [])
        if business_insights:
            report.append("## 💡 Strategic Recommendations")
            for i, insight in enumerate(business_insights, 1):
                report.append(f"{i}. {insight}")
            report.append("")
        
        # Quality Gates and Metrics
        report.append("## 📊 Quality Gates Assessment")
        
        overall_pass_rate = ((total_tests - failed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        gates = [
            ("Overall Pass Rate", overall_pass_rate, 95, "% passed"),
            ("Critical Flow Health", min([h['health_score'] for h in critical_flows.values()]) if critical_flows else 100, 90, "% healthy"),
            ("Feature Coverage", len([f for f in feature_breakdown.values() if f['total'] > 0]), len(feature_breakdown), " features covered")
        ]
        
        for gate_name, current, target, unit in gates:
            status = "✅ PASS" if current >= target else "❌ FAIL"
            report.append(f"- **{gate_name}**: {current:.1f}{unit} (Target: {target}{unit}) {status}")
        
        report.append("")
        
        # Next Steps for Business
        report.append("## 🚀 Immediate Next Steps")
        
        if failed_tests > total_tests * 0.1:  # More than 10% failure rate
            report.append("### High Priority:")
            report.append("1. **Immediate**: Review all critical business flow failures")
            report.append("2. **Today**: Assign developers to feature areas with <80% pass rate")
            report.append("3. **This Week**: Implement fixes and re-run affected test suites")
        else:
            report.append("### Maintenance Priority:")
            report.append("1. **Monitor**: Continue tracking quality metrics")
            report.append("2. **Optimize**: Address any remaining slow or flaky tests")
            report.append("3. **Expand**: Consider adding more test coverage to identified gaps")
        
        report.append("")
        report.append("---")
        report.append(f"*Report generated by Enhanced Test Analyzer v2.1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(report)
    
    def _assess_business_risk(self, business_analysis: Dict[str, Any], failed_tests: int, total_tests: int) -> str:
        """Assess overall business risk level"""
        
        failure_rate = (failed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Check critical flows
        critical_flows = business_analysis.get('critical_flow_health', {})
        critical_risk_flows = sum(1 for flow in critical_flows.values() if flow['risk_level'] in ['High', 'Critical'])
        
        if failure_rate > 20 or critical_risk_flows > 0:
            return "🔴 HIGH - Immediate action required"
        elif failure_rate > 10:
            return "🟡 MEDIUM - Monitor closely"
        else:
            return "🟢 LOW - Normal operations"
    
    def save_enhanced_csv(self, enhanced_results: List[Dict[str, Any]], csv_file: str):
        """Save enhanced test results as CSV"""
        import csv
        
        if not enhanced_results:
            return
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'test_name', 'status', 'duration_seconds', 'environment',
                'failure_category', 'failure_hint', 'confidence_score',
                'category_reasoning', 'environment_source'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for test in enhanced_results:
                row = {field: test.get(field, '') for field in fieldnames}
                writer.writerow(row)
    
    def generate_basic_analysis(self, results):
        """Fallback method for basic analysis"""
        total_tests = len(results)
        failed_tests = sum(1 for test in results if test.get('status') == 'failed')
        passed_tests = total_tests - failed_tests
        
        return {
            'total_tests': total_tests,
            'failed_tests': failed_tests,
            'passed_tests': passed_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'enhanced_analysis_available': False
        }

def main():
    parser = argparse.ArgumentParser(
        description="Analyze test logs from local directory with enhanced categorization, environment mapping, and performance analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhanced analysis (default)
  python local_analyzer.py --input "C:\\test-results"
  
  # With notifications
  python local_analyzer.py --input "C:\\test-results" --notify
  
  # Custom output directory
  python local_analyzer.py --input "C:\\test-results" --output "C:\\reports"
  
  # Basic analysis only (no enhanced features)
  python local_analyzer.py --input "C:\\test-results" --basic
  
  # Generate comprehensive reports
  python local_analyzer.py --input "C:\\test-results" --enhanced-reports
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input directory containing test log files'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output directory for reports (default: ./output/reports)'
    )
    
    parser.add_argument(
        '--notify', '-n',
        action='store_true',
        help='Send notifications (requires .env configuration)'
    )
    
    parser.add_argument(
        '--basic', '-b',
        action='store_true',
        help='Basic analysis only (no enhanced features)'
    )
    
    parser.add_argument(
        '--enhanced-reports',
        action='store_true',
        help='Generate comprehensive enhanced reports with all analytics'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        default='*.json',
        help='File pattern to match (default: *.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize analyzer
        analyzer = LocalTestAnalyzer(args.input, args.output)
        
        # Run analysis
        result = analyzer.analyze_local_files(
            send_notifications=args.notify,
            generate_reports=True,  # Always generate some reports
            use_enhanced=not args.basic
        )
        
        if result:
            print(f"\n✅ Analysis completed successfully!")
            print(f"📊 Reports saved to: {analyzer.output_dir}")
            
            if not args.basic and result.get('improvements'):
                improvements = result['improvements']
                if improvements.get('improvement_count', 0) > 0:
                    print(f"🎯 Enhanced features resolved {improvements['improvement_count']} unknown categories!")
        else:
            print("\n❌ Analysis failed or no results found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Analysis cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()