"""
Enhanced Test Analysis Integration
Combines enhanced categorization, environment mapping, and performance analytics
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from enhanced_test_analyzer import EnhancedTestAnalyzer
from performance_analyzer import PerformanceAnalyzer


class IntegratedTestAnalyzer:
    """
    Main analyzer that integrates all enhanced features:
    - Enhanced failure categorization
    - Environment mapping
    - Performance analytics
    - Comprehensive reporting
    """

    def __init__(self):
        self.enhanced_analyzer = EnhancedTestAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()

    def analyze_test_data(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive analysis combining all enhanced features
        """
        if not test_results:
            return {'error': 'No test data provided'}

        print(f"🔍 Starting comprehensive analysis of {len(test_results)} tests...")

        # Step 1: Enhance individual test results
        enhanced_results = []
        unknown_before = 0
        unknown_after = 0

        for test in test_results:
            # Get enhanced analysis for this test
            enhanced_test = self.enhanced_analyzer.enhance_test_result(test)
            enhanced_results.append(enhanced_test)

            # Track improvement in categorization
            original_category = test.get('failure_category', 'unknown')
            new_category = enhanced_test.get('failure_category', 'unknown')

            if original_category.lower() in ['unknown', 'other', 'n/a']:
                unknown_before += 1
            if new_category.lower() in ['unknown', 'other', 'n/a']:
                unknown_after += 1

        # Step 2: Perform performance analysis
        performance_analysis = self.performance_analyzer.analyze_test_durations(enhanced_results)

        # Step 3: Generate comprehensive summary
        summary = self._generate_comprehensive_summary(enhanced_results, performance_analysis)

        # Step 4: Track improvements
        improvements = {
            'categorization_improvement': {
                'unknown_before': unknown_before,
                'unknown_after': unknown_after,
                'improvement_count': unknown_before - unknown_after,
                'improvement_percentage': (
                    (unknown_before - unknown_after) / len(test_results) * 100) if test_results else 0}}

        return {
            'enhanced_results': enhanced_results,
            'performance_analysis': performance_analysis,
            'summary': summary,
            'improvements': improvements,
            'metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_tests': len(enhanced_results),
                'analyzer_version': '2.0.0'
            }
        }

    def _generate_comprehensive_summary(self, enhanced_results: List[Dict[str, Any]],
                                        performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive summary of all analysis results"""

        # Basic statistics
        total_tests = len(enhanced_results)
        passed_tests = sum(1 for test in enhanced_results if test.get('status') == 'passed')
        failed_tests = sum(1 for test in enhanced_results if test.get('status') == 'failed')

        # Enhanced categorization summary
        category_counts = {}
        environment_counts = {}
        failure_hints = []

        for test in enhanced_results:
            # Count categories
            category = test.get('failure_category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

            # Count environments
            env = test.get('environment', 'unknown')
            environment_counts[env] = environment_counts.get(env, 0) + 1

            # Collect failure hints
            hint = test.get('failure_hint')
            if hint and test.get('status') == 'failed':
                failure_hints.append({
                    'test_name': test.get('test_name', 'Unknown'),
                    'category': category,
                    'hint': hint,
                    'environment': env
                })

        # Environment distribution
        env_performance = {}
        if 'duration_by_environment' in performance_analysis:
            env_performance = performance_analysis['duration_by_environment']

        summary = {
            'test_statistics': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'pass_rate_percentage': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'fail_rate_percentage': (failed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'enhanced_categorization': {
                'category_distribution': category_counts,
                'most_common_failure_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else 'none',
                'unique_categories_identified': len(category_counts),
                'actionable_hints_generated': len(failure_hints)
            },
            'environment_analysis': {
                'environment_distribution': environment_counts,
                'environments_identified': list(environment_counts.keys()),
                'environment_performance': env_performance
            },
            'failure_insights': {
                'top_failure_hints': failure_hints[:10],  # Top 10 most actionable hints
                'critical_issues': [hint for hint in failure_hints if 'critical' in hint.get('hint', '').lower()],
                'performance_related_failures': [
                    hint for hint in failure_hints
                    if any(perf_word in hint.get('hint', '').lower() for perf_word in ['timeout', 'slow', 'performance'])
                ]
            }
        }

        return summary

    def generate_enhanced_report(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a comprehensive report with all enhancements"""

        if 'error' in analysis_result:
            return f"Analysis Error: {analysis_result['error']}"

        report = []
        report.append("# 🚀 Enhanced Test Analysis Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Executive Summary
        summary = analysis_result.get('summary', {})
        stats = summary.get('test_statistics', {})

        report.append("## 📊 Executive Summary")
        report.append(f"- **Total Tests**: {stats.get('total_tests', 0)}")
        report.append(f"- **Pass Rate**: {stats.get('pass_rate_percentage', 0):.1f}%")
        report.append(f"- **Failed Tests**: {stats.get('failed_tests', 0)}")
        report.append("")

        # Improvements Made
        improvements = analysis_result.get('improvements', {})
        cat_improvement = improvements.get('categorization_improvement', {})

        report.append("## 🎯 Analysis Improvements")
        report.append(f"- **Unknown Categories Resolved**: {cat_improvement.get('improvement_count', 0)}")
        report.append(f"- **Categorization Improvement**: {cat_improvement.get('improvement_percentage', 0):.1f}%")
        report.append(f"- **Remaining Unknown**: {cat_improvement.get('unknown_after', 0)} tests")
        report.append("")

        # Enhanced Categorization
        cat_data = summary.get('enhanced_categorization', {})
        report.append("## 🏷️ Enhanced Failure Categories")
        category_dist = cat_data.get('category_distribution', {})

        for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats.get('total_tests', 1)) * 100
            report.append(f"- **{category.replace('_', ' ').title()}**: {count} tests ({percentage:.1f}%)")

        report.append(
            f"\n*Most Common Issue*: {cat_data.get('most_common_failure_category', 'N/A').replace('_', ' ').title()}")
        report.append("")

        # Environment Analysis
        env_data = summary.get('environment_analysis', {})
        report.append("## 🌍 Environment Analysis")

        env_dist = env_data.get('environment_distribution', {})
        for env, count in sorted(env_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats.get('total_tests', 1)) * 100
            report.append(f"- **{env.capitalize()}**: {count} tests ({percentage:.1f}%)")

        # Environment Performance
        env_perf = env_data.get('environment_performance', {})
        if env_perf:
            report.append("\n### Environment Performance:")
            for env, perf_data in sorted(env_perf.items(), key=lambda x: x[1]['average_seconds']):
                report.append(f"- **{env.capitalize()}**: {perf_data['average_seconds']:.1f}s average")
        report.append("")

        # Performance Analysis
        perf_analysis = analysis_result.get('performance_analysis', {})
        if perf_analysis and 'error' not in perf_analysis:
            report.append("## ⚡ Performance Insights")
            report.append(f"- **Average Duration**: {perf_analysis.get('average_duration_seconds', 0):.1f} seconds")
            report.append(
                f"- **Total Execution Time**: {perf_analysis.get('total_execution_time_minutes', 0):.1f} minutes")

            perf_dist = perf_analysis.get('performance_percentages', {})
            report.append(f"- **Fast Tests** (<5s): {perf_dist.get('fast', 0):.1f}%")
            report.append(f"- **Slow Tests** (>30s): {perf_dist.get('slow', 0) + perf_dist.get('very_slow', 0):.1f}%")
            report.append("")

        # Top Actionable Insights
        failure_insights = summary.get('failure_insights', {})
        top_hints = failure_insights.get('top_failure_hints', [])

        if top_hints:
            report.append("## 💡 Top Actionable Insights")
            for i, hint_data in enumerate(top_hints[:5], 1):
                report.append(f"{i}. **{hint_data['test_name']}** ({hint_data['category']}):")
                report.append(f"   {hint_data['hint']}")
                report.append(f"   *Environment: {hint_data['environment']}*")
                report.append("")

        # Critical Issues
        critical_issues = failure_insights.get('critical_issues', [])
        if critical_issues:
            report.append("## 🚨 Critical Issues Identified")
            for issue in critical_issues[:3]:
                report.append(f"- **{issue['test_name']}**: {issue['hint']}")
            report.append("")

        # Performance-Related Failures
        perf_failures = failure_insights.get('performance_related_failures', [])
        if perf_failures:
            report.append("## 🐌 Performance-Related Failures")
            for failure in perf_failures[:3]:
                report.append(f"- **{failure['test_name']}**: {failure['hint']}")
            report.append("")

        # Add performance report if available
        if perf_analysis and 'error' not in perf_analysis:
            performance_report = self.performance_analyzer.generate_performance_report(perf_analysis)
            report.append("\n" + "=" * 60)
            report.append(performance_report)

        return "\n".join(report)

    def save_enhanced_results(self, analysis_result: Dict[str, Any], output_dir: str = "enhanced_analysis"):
        """Save enhanced analysis results to files"""

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results as JSON
        json_file = os.path.join(output_dir, f"enhanced_analysis_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, default=str)

        # Save comprehensive report
        report = self.generate_enhanced_report(analysis_result)
        report_file = os.path.join(output_dir, f"enhanced_report_{timestamp}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        # Save CSV of enhanced test results for further analysis
        csv_file = os.path.join(output_dir, f"enhanced_tests_{timestamp}.csv")
        self._save_enhanced_csv(analysis_result.get('enhanced_results', []), csv_file)

        return {
            'json_file': json_file,
            'report_file': report_file,
            'csv_file': csv_file
        }

    def _save_enhanced_csv(self, enhanced_results: List[Dict[str, Any]], csv_file: str):
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
