"""
Advanced Metrics Analyzer
Provides additional business-focused and operational metrics for test analysis
"""

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import statistics


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

        # Performance thresholds for different test types
        self.performance_benchmarks = {
            'unit_tests': {'target': 1000, 'acceptable': 5000},      # 1s target, 5s acceptable
            'integration_tests': {'target': 10000, 'acceptable': 30000},  # 10s target, 30s acceptable
            'e2e_tests': {'target': 30000, 'acceptable': 120000},    # 30s target, 2min acceptable
            'ui_tests': {'target': 15000, 'acceptable': 60000}       # 15s target, 1min acceptable
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
                critical_flow_health[flow_name] = {
                    'total_tests': total_flow_tests,
                    'passed_tests': passed_flow_tests,
                    'health_score': (
                        passed_flow_tests /
                        total_flow_tests *
                        100) if total_flow_tests > 0 else 0,
                    'risk_level': self._calculate_risk_level(
                        passed_flow_tests /
                        total_flow_tests *
                        100 if total_flow_tests > 0 else 0)}

        return {
            'feature_breakdown': dict(feature_breakdown),
            'critical_flow_health': critical_flow_health,
            'business_insights': self._generate_business_insights(feature_breakdown, critical_flow_health)
        }

    def analyze_test_reliability(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test reliability and stability metrics"""

        # Group tests by name to detect patterns
        test_patterns = defaultdict(list)
        for test in test_results:
            test_name = test.get('test_name', '')
            test_patterns[test_name].append(test)

        reliability_metrics = {
            'total_unique_tests': len(test_patterns),
            'potentially_flaky_tests': [],
            'most_reliable_tests': [],
            'retry_analysis': {'tests_with_retries': 0, 'total_retries': 0}
        }

        # Analyze each test pattern
        for test_name, test_instances in test_patterns.items():
            if len(test_instances) > 1:
                # Multiple instances - check for flakiness
                statuses = [t.get('status') for t in test_instances]
                unique_statuses = set(statuses)

                if len(unique_statuses) > 1:
                    # Flaky test detected
                    reliability_metrics['potentially_flaky_tests'].append({
                        'test_name': test_name,
                        'run_count': len(test_instances),
                        'pass_count': statuses.count('passed'),
                        'fail_count': statuses.count('failed'),
                        'reliability_score': (statuses.count('passed') / len(statuses)) * 100
                    })

            # Check for retries
            for test in test_instances:
                retries = test.get('retries_count', 0)
                if retries > 0:
                    reliability_metrics['retry_analysis']['tests_with_retries'] += 1
                    reliability_metrics['retry_analysis']['total_retries'] += retries

        # Find most reliable tests (single instance, passed)
        for test_name, test_instances in test_patterns.items():
            if len(test_instances) == 1 and test_instances[0].get('status') == 'passed':
                reliability_metrics['most_reliable_tests'].append({
                    'test_name': test_name,
                    'duration_seconds': test_instances[0].get('duration_seconds', 0)
                })

        # Sort and limit results
        reliability_metrics['potentially_flaky_tests'].sort(key=lambda x: x['reliability_score'])
        reliability_metrics['most_reliable_tests'].sort(key=lambda x: x['duration_seconds'])

        return reliability_metrics

    def analyze_performance_trends(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Advanced performance analysis with trends and benchmarks"""

        durations = [t.get('duration_ms', 0) for t in test_results if t.get('duration_ms', 0) > 0]
        if not durations:
            return {'error': 'No duration data available'}

        # Calculate percentiles
        percentiles = {
            'p50': statistics.median(durations),
            'p75': statistics.quantiles(durations, n=4)[2] if len(durations) > 4 else statistics.median(durations),
            'p90': statistics.quantiles(durations, n=10)[8] if len(durations) > 10 else max(durations),
            'p95': statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else max(durations),
            'p99': statistics.quantiles(durations, n=100)[98] if len(durations) > 100 else max(durations)
        }

        # Performance by test type (inferred from test name patterns)
        test_type_performance = defaultdict(list)
        for test in test_results:
            test_name = test.get('test_name', '').lower()
            duration_ms = test.get('duration_ms', 0)

            if duration_ms > 0:
                # Infer test type from name patterns
                if 'unit' in test_name or test_name.endswith('_test'):
                    test_type_performance['unit_tests'].append(duration_ms)
                elif 'integration' in test_name or 'api' in test_name:
                    test_type_performance['integration_tests'].append(duration_ms)
                elif 'e2e' in test_name or 'end_to_end' in test_name:
                    test_type_performance['e2e_tests'].append(duration_ms)
                else:
                    test_type_performance['ui_tests'].append(duration_ms)  # Default assumption for UI automation

        # Benchmark analysis
        benchmark_analysis = {}
        for test_type, durations_list in test_type_performance.items():
            if durations_list and test_type in self.performance_benchmarks:
                avg_duration = statistics.mean(durations_list)
                benchmark = self.performance_benchmarks[test_type]

                benchmark_analysis[test_type] = {
                    'average_duration_ms': avg_duration,
                    'test_count': len(durations_list),
                    'target_ms': benchmark['target'],
                    'acceptable_ms': benchmark['acceptable'],
                    'vs_target': f"{(avg_duration / benchmark['target'] * 100):.1f}% of target",
                    'performance_status': self._get_performance_status(avg_duration, benchmark)
                }

        # Slowest tests analysis
        slow_tests = []
        for test in test_results:
            duration_ms = test.get('duration_ms', 0)
            if duration_ms > 60000:  # Slower than 1 minute
                slow_tests.append({
                    'test_name': test.get('test_name'),
                    'duration_seconds': test.get('duration_seconds', 0),
                    'status': test.get('status'),
                    'failure_category': test.get('failure_category', 'n/a')
                })

        slow_tests.sort(key=lambda x: x['duration_seconds'], reverse=True)

        return {
            'percentiles_ms': percentiles,
            'percentiles_seconds': {k: v / 1000 for k, v in percentiles.items()},
            'test_type_performance': benchmark_analysis,
            'slowest_tests': slow_tests[:10],
            'performance_recommendations': self._generate_performance_recommendations(benchmark_analysis, slow_tests)
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

            # Extract keywords from failure reasons
            words = re.findall(r'\b\w+\b', failure_reason)
            significant_words = [
                w for w in words if len(w) > 3 and w not in [
                    'test', 'should', 'have', 'when', 'with', 'this', 'that']]
            failure_patterns['common_error_keywords'].update(significant_words)

            # Categorize specific failure types
            if any(keyword in failure_reason for keyword in ['element', 'selector', 'locator', 'click', 'visible']):
                failure_patterns['element_interaction_issues'].append({
                    'test_name': test_name,
                    'issue': 'Element interaction failure',
                    'suggestion': 'Review page object model and element selectors'
                })

            if any(keyword in failure_reason for keyword in ['timeout', 'wait', 'delay', 'slow']):
                failure_patterns['timing_related_failures'].append({
                    'test_name': test_name,
                    'issue': 'Timing/wait issue',
                    'suggestion': 'Implement better wait strategies or increase timeouts'
                })

            if any(keyword in failure_reason for keyword in ['expected', 'actual', 'assert', 'match']):
                failure_patterns['data_validation_failures'].append({
                    'test_name': test_name,
                    'issue': 'Data validation failure',
                    'suggestion': 'Review test data setup and application state'
                })

        # Get top error keywords
        top_keywords = failure_patterns['common_error_keywords'].most_common(10)

        return {
            'total_failed_tests': len(failed_tests),
            'top_error_keywords': top_keywords,
            'element_interaction_issues': failure_patterns['element_interaction_issues'][:5],
            'timing_related_failures': failure_patterns['timing_related_failures'][:5],
            'data_validation_failures': failure_patterns['data_validation_failures'][:5],
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

    def _get_performance_status(self, avg_duration: float, benchmark: Dict[str, int]) -> str:
        """Get performance status based on benchmarks"""
        if avg_duration <= benchmark['target']:
            return 'Excellent'
        elif avg_duration <= benchmark['acceptable']:
            return 'Acceptable'
        else:
            return 'Needs Improvement'

    def _generate_business_insights(self, feature_breakdown: Dict, critical_flow_health: Dict) -> List[str]:
        """Generate business-focused insights"""
        insights = []

        # Feature area insights
        for feature, data in feature_breakdown.items():
            if data['total'] > 0 and data['pass_rate'] < 80:
                insights.append(f"{feature.replace('_',
                                                   ' ').title()} area has {data['pass_rate']:.1f}% pass rate - needs attention")

        # Critical flow insights
        for flow, health in critical_flow_health.items():
            if health['risk_level'] in ['High', 'Critical']:
                insights.append(
                    f"{
                        flow.replace(
                            '_', ' ').title()} flow is at {
                        health['risk_level'].lower()} risk with {
                        health['health_score']:.1f}% health")

        return insights

    def _generate_performance_recommendations(self, benchmark_analysis: Dict, slow_tests: List) -> List[str]:
        """Generate performance-specific recommendations"""
        recommendations = []

        for test_type, analysis in benchmark_analysis.items():
            if analysis['performance_status'] == 'Needs Improvement':
                recommendations.append(
                    f"{test_type.replace('_', ' ').title()} are running {analysis['vs_target']} - optimize or review thresholds")

        if len(slow_tests) > 5:
            recommendations.append(
                f"{len(slow_tests)} tests taking >1 minute - consider breaking into smaller tests or parallelization")

        return recommendations

    def _generate_failure_insights(self, failure_patterns: Dict, top_keywords: List) -> List[str]:
        """Generate failure-specific insights"""
        insights = []

        if top_keywords:
            top_keyword = top_keywords[0][0]
            insights.append(f"Most common failure keyword: '{top_keyword}' - focus debugging efforts here")

        element_issues = len(failure_patterns['element_interaction_issues'])
        if element_issues > 0:
            insights.append(f"{element_issues} tests failing on element interactions - UI changes may have occurred")

        timing_issues = len(failure_patterns['timing_related_failures'])
        if timing_issues > 0:
            insights.append(
                f"{timing_issues} tests failing on timing - consider performance optimization or wait strategy review")

        return insights
