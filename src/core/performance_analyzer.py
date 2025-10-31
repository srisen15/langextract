"""
Performance Analytics Module
Provides detailed insights into test execution performance
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime
import statistics

class PerformanceAnalyzer:
    """Analyzes test performance metrics and provides insights"""
    
    def __init__(self):
        self.performance_thresholds = {
            'fast': 5000,      # < 5 seconds
            'normal': 30000,   # < 30 seconds  
            'slow': 60000,     # < 1 minute
            'very_slow': float('inf')  # >= 1 minute
        }
    
    def analyze_test_durations(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive analysis of test execution durations"""
        
        if not test_results:
            return {}
        
        # Extract durations
        durations = []
        duration_by_status = {'passed': [], 'failed': []}
        duration_by_category = {}
        duration_by_environment = {}
        
        for test in test_results:
            duration_ms = test.get('duration_ms', 0)
            duration_seconds = test.get('duration_seconds', 0)
            
            if duration_ms > 0:
                durations.append(duration_ms)
                
                # Group by status
                status = test.get('status', 'unknown')
                if status in duration_by_status:
                    duration_by_status[status].append(duration_ms)
                
                # Group by failure category
                category = test.get('failure_category', 'N/A')
                if category not in duration_by_category:
                    duration_by_category[category] = []
                duration_by_category[category].append(duration_ms)
                
                # Group by environment
                env = test.get('environment', 'unknown')
                if env not in duration_by_environment:
                    duration_by_environment[env] = []
                duration_by_environment[env].append(duration_ms)
        
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
            'duration_std_dev': statistics.stdev(durations) if len(durations) > 1 else 0,
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
        
        # Find extreme tests
        analysis['performance_insights'] = self._get_performance_insights(test_results, durations)
        
        # Duration by status comparison
        analysis['duration_by_status'] = {}
        for status, status_durations in duration_by_status.items():
            if status_durations:
                analysis['duration_by_status'][status] = {
                    'count': len(status_durations),
                    'average_ms': statistics.mean(status_durations),
                    'average_seconds': statistics.mean(status_durations) / 1000,
                    'median_ms': statistics.median(status_durations),
                    'total_time_minutes': sum(status_durations) / 60000
                }
        
        # Duration by environment
        analysis['duration_by_environment'] = {}
        for env, env_durations in duration_by_environment.items():
            if env_durations and len(env_durations) >= 3:  # Only include envs with meaningful data
                analysis['duration_by_environment'][env] = {
                    'count': len(env_durations),
                    'average_ms': statistics.mean(env_durations),
                    'average_seconds': statistics.mean(env_durations) / 1000,
                    'median_ms': statistics.median(env_durations)
                }
        
        return analysis
    
    def _get_performance_insights(self, test_results: List[Dict[str, Any]], durations: List[int]) -> Dict[str, Any]:
        """Extract specific performance insights and recommendations"""
        
        insights = {}
        
        # Find fastest and slowest tests
        fastest_test = min(test_results, key=lambda x: x.get('duration_ms', float('inf')))
        slowest_test = max(test_results, key=lambda x: x.get('duration_ms', 0))
        
        insights['fastest_test'] = {
            'name': fastest_test.get('test_name', 'Unknown'),
            'duration_ms': fastest_test.get('duration_ms', 0),
            'duration_seconds': fastest_test.get('duration_seconds', 0),
            'environment': fastest_test.get('environment', 'unknown'),
            'status': fastest_test.get('status', 'unknown')
        }
        
        insights['slowest_test'] = {
            'name': slowest_test.get('test_name', 'Unknown'),
            'duration_ms': slowest_test.get('duration_ms', 0),
            'duration_seconds': slowest_test.get('duration_seconds', 0),
            'environment': slowest_test.get('environment', 'unknown'),
            'status': slowest_test.get('status', 'unknown'),
            'failure_category': slowest_test.get('failure_category', 'N/A')
        }
        
        # Find tests that are significantly slower than average
        avg_duration = statistics.mean(durations)
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0
        threshold = avg_duration + (2 * std_dev)  # 2 standard deviations above mean
        
        slow_outliers = [
            test for test in test_results 
            if test.get('duration_ms', 0) > threshold and test.get('duration_ms', 0) > 30000
        ]
        
        insights['slow_outliers'] = []
        for test in slow_outliers[:5]:  # Top 5 slow outliers
            insights['slow_outliers'].append({
                'name': test.get('test_name', 'Unknown'),
                'duration_seconds': test.get('duration_seconds', 0),
                'environment': test.get('environment', 'unknown'),
                'status': test.get('status', 'unknown'),
                'times_slower_than_avg': test.get('duration_ms', 0) / avg_duration
            })
        
        # Performance recommendations
        insights['recommendations'] = self._generate_performance_recommendations(
            durations, insights['performance_distribution'] if 'performance_distribution' in insights else {}
        )
        
        return insights
    
    def _generate_performance_recommendations(self, durations: List[int], distribution: Dict[str, int]) -> List[str]:
        """Generate actionable performance recommendations"""
        recommendations = []
        
        avg_duration = statistics.mean(durations)
        very_slow_count = sum(1 for d in durations if d > 60000)
        slow_count = sum(1 for d in durations if 30000 < d <= 60000)
        
        # High-level recommendations
        if avg_duration > 30000:
            recommendations.append("Average test duration is high (>30s). Consider optimizing test scenarios.")
        
        if very_slow_count > len(durations) * 0.1:  # More than 10% very slow
            recommendations.append(f"{very_slow_count} tests take over 1 minute. Review these for optimization opportunities.")
        
        if slow_count > len(durations) * 0.2:  # More than 20% slow
            recommendations.append("Many tests are running slowly. Check for inefficient waits and page loads.")
        
        # Specific recommendations
        slow_percentage = (slow_count + very_slow_count) / len(durations) * 100
        if slow_percentage > 30:
            recommendations.extend([
                "Consider parallel test execution to reduce overall runtime",
                "Review explicit waits and replace with more efficient waiting strategies",
                "Optimize test data setup and teardown processes"
            ])
        
        if not recommendations:
            recommendations.append("Test performance looks good! Most tests complete in reasonable time.")
        
        return recommendations
    
    def generate_performance_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive performance report"""
        
        if 'error' in analysis:
            return f"Performance Analysis Error: {analysis['error']}"
        
        report = []
        report.append("# 🚀 Test Performance Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        # Executive Summary
        report.append("## 📊 Executive Summary")
        report.append(f"- **Total Tests Analyzed**: {analysis['total_tests_analyzed']}")
        report.append(f"- **Total Execution Time**: {analysis['total_execution_time_minutes']:.1f} minutes")
        report.append(f"- **Average Test Duration**: {analysis['average_duration_seconds']:.1f} seconds")
        report.append(f"- **Median Test Duration**: {analysis['median_duration_seconds']:.1f} seconds")
        report.append("")
        
        # Performance Distribution
        report.append("## ⚡ Performance Distribution")
        dist = analysis.get('performance_percentages', {})
        report.append(f"- **Fast Tests** (<5s): {dist.get('fast', 0):.1f}%")
        report.append(f"- **Normal Tests** (5-30s): {dist.get('normal', 0):.1f}%")
        report.append(f"- **Slow Tests** (30-60s): {dist.get('slow', 0):.1f}%")
        report.append(f"- **Very Slow Tests** (>60s): {dist.get('very_slow', 0):.1f}%")
        report.append("")
        
        # Extreme Tests
        insights = analysis.get('performance_insights', {})
        if insights:
            report.append("## 🏆 Performance Extremes")
            
            fastest = insights.get('fastest_test', {})
            report.append(f"**Fastest Test**: `{fastest.get('name', 'N/A')}` - {fastest.get('duration_seconds', 0):.2f}s")
            
            slowest = insights.get('slowest_test', {})
            report.append(f"**Slowest Test**: `{slowest.get('name', 'N/A')}` - {slowest.get('duration_seconds', 0):.2f}s")
            report.append("")
            
            # Slow Outliers
            outliers = insights.get('slow_outliers', [])
            if outliers:
                report.append("### 🐌 Slow Test Outliers")
                for outlier in outliers:
                    report.append(f"- `{outlier['name']}`: {outlier['duration_seconds']:.1f}s "
                                f"({outlier['times_slower_than_avg']:.1f}x slower than average)")
                report.append("")
        
        # Environment Performance
        env_data = analysis.get('duration_by_environment', {})
        if env_data:
            report.append("## 🌍 Performance by Environment")
            for env, data in sorted(env_data.items(), key=lambda x: x[1]['average_seconds'], reverse=True):
                report.append(f"- **{env.capitalize()}**: {data['average_seconds']:.1f}s avg "
                            f"({data['count']} tests)")
            report.append("")
        
        # Status Performance
        status_data = analysis.get('duration_by_status', {})
        if status_data:
            report.append("## 📈 Performance by Test Status")
            for status, data in status_data.items():
                report.append(f"- **{status.capitalize()} Tests**: {data['average_seconds']:.1f}s avg "
                            f"({data['count']} tests, {data['total_time_minutes']:.1f}min total)")
            report.append("")
        
        # Recommendations
        recommendations = insights.get('recommendations', [])
        if recommendations:
            report.append("## 💡 Performance Recommendations")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        return "\n".join(report)