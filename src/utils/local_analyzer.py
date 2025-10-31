#!/usr/bin/env python3
"""
Local Test Log Analyzer - Enhanced Version
Analyzes test logs from local directories with all the advanced features
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Import our existing modules
try:
    # Try relative imports first (when run as module)
    from ..core.test_log_analyzer import TestLogExtractor, BatchTestAnalyzer
    from ..core.automated_scheduler import TestAnalysisScheduler
    from ..core.integrated_analyzer import IntegratedTestAnalyzer
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
        from core.integrated_analyzer import IntegratedTestAnalyzer
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("💡 Make sure you're in the correct directory and have run the setup script")
        print("💡 Try running: .\\scripts\\setup.ps1")
        sys.exit(1)

class LocalTestAnalyzer:
    """Enhanced local test log analyzer with all production features"""
    
    def __init__(self, input_dir, output_dir=None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else Path("./output/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize batch analyzer with input directory
        self.batch_analyzer = BatchTestAnalyzer(str(self.input_dir))
        
        # Initialize enhanced integrated analyzer
        self.integrated_analyzer = IntegratedTestAnalyzer()
        
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
    
    def analyze_local_files(self, send_notifications=False, generate_reports=True):
        """
        Analyze local test files with enhanced categorization, environment mapping, and performance analytics
        
        Args:
            send_notifications: Whether to send notifications (requires .env setup)
            generate_reports: Whether to generate detailed reports
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
            
            print(f"\n🚀 Applying enhanced analysis to {len(results)} test results...")
            
            # Run enhanced integrated analysis
            enhanced_analysis = self.integrated_analyzer.analyze_test_data(results)
            
            if 'error' in enhanced_analysis:
                print(f"❌ Enhanced analysis failed: {enhanced_analysis['error']}")
                # Fall back to basic analysis
                analysis = self.generate_basic_analysis(results)
            else:
                # Display enhanced summary
                self.display_enhanced_summary(enhanced_analysis)
                
                if generate_reports:
                    # Generate enhanced reports
                    report_files = self.generate_enhanced_reports(enhanced_analysis)
                    print(f"\n📊 Enhanced reports generated:")
                    for report_file in report_files:
                        print(f"   - {report_file}")
                
                if send_notifications:
                    # Send notifications with enhanced data
                    self.send_enhanced_notifications(enhanced_analysis)
                
                return enhanced_analysis
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            print(f"❌ Analysis failed: {e}")
            return None
    
    def display_summary(self, analysis):
        """Display analysis summary to console"""
        print("\n" + "="*60)
        print("📊 LOCAL TEST ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📁 Source Directory: {self.input_dir}")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Basic metrics
        total_tests = analysis['total_tests']
        failed_tests = analysis['failed_tests']
        passed_tests = analysis['passed_tests']
        failure_rate = analysis['failure_rate']
        pass_rate = 100 - failure_rate
        
        print(f"🎯 EXECUTION METRICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({pass_rate:.1f}%)")
        print(f"   Failed: {failed_tests} ({failure_rate:.1f}%)")
        print()
        
        # Failure breakdown
        if analysis.get('category_breakdown'):
            print(f"🚨 FAILURE CATEGORIES:")
            for category, count in analysis['category_breakdown'].items():
                percentage = (count / failed_tests * 100) if failed_tests > 0 else 0
                print(f"   - {category}: {count} failures ({percentage:.1f}%)")
            print()
        
        # High priority issues
        needs_attention = analysis.get('needs_attention', 0)
        if needs_attention > 0:
            print(f"⚠️  NEEDS ATTENTION: {needs_attention} failures require immediate attention")
            print()
        
        # Flaky tests
        flaky_tests = analysis.get('flaky_tests', 0)
        if flaky_tests > 0:
            print(f"🔄 FLAKY TESTS: {flaky_tests} tests show inconsistent behavior")
            print()
        
        # Environment breakdown
        environments = analysis.get('environments', [])
        if environments:
            print(f"🌍 ENVIRONMENTS: {', '.join(environments)}")
            print()
        
        print("\n" + "="*60)
    
    def display_enhanced_summary(self, enhanced_analysis):
        """Display enhanced analysis summary to console with all new features"""
        print("\n" + "="*80)
        print("🚀 ENHANCED TEST ANALYSIS SUMMARY")
        print("="*80)
        
        metadata = enhanced_analysis.get('metadata', {})
        summary = enhanced_analysis.get('summary', {})
        improvements = enhanced_analysis.get('improvements', {})
        
        print(f"📁 Source Directory: {self.input_dir}")
        print(f"📅 Analysis Date: {metadata.get('analysis_timestamp', 'Unknown')}")
        print(f"🔧 Analyzer Version: {metadata.get('analyzer_version', '2.0.0')}")
        print()
        
        # Basic metrics with enhanced data
        stats = summary.get('test_statistics', {})
        print(f"🎯 EXECUTION METRICS:")
        print(f"   Total Tests: {stats.get('total_tests', 0)}")
        print(f"   Passed: {stats.get('passed_tests', 0)} ({stats.get('pass_rate_percentage', 0):.1f}%)")
        print(f"   Failed: {stats.get('failed_tests', 0)} ({stats.get('fail_rate_percentage', 0):.1f}%)")
        print()
        
        # Show improvements made by enhanced analyzer
        cat_improvement = improvements.get('categorization_improvement', {})
        if cat_improvement.get('improvement_count', 0) > 0:
            print(f"✨ ENHANCED CATEGORIZATION IMPROVEMENTS:")
            print(f"   Unknown Categories Resolved: {cat_improvement.get('improvement_count', 0)}")
            print(f"   Improvement Rate: {cat_improvement.get('improvement_percentage', 0):.1f}%")
            print(f"   Remaining Unknown: {cat_improvement.get('unknown_after', 0)} tests")
            print()
        
        # Enhanced failure categories
        enhanced_cat = summary.get('enhanced_categorization', {})
        category_dist = enhanced_cat.get('category_distribution', {})
        if category_dist:
            print(f"🏷️ ENHANCED FAILURE CATEGORIES:")
            for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats.get('total_tests', 1)) * 100
                category_display = category.replace('_', ' ').title()
                print(f"   - {category_display}: {count} tests ({percentage:.1f}%)")
            
            most_common = enhanced_cat.get('most_common_failure_category', '').replace('_', ' ').title()
            print(f"\n   Most Common Issue: {most_common}")
            print(f"   Actionable Hints Generated: {enhanced_cat.get('actionable_hints_generated', 0)}")
            print()
        
        # Environment analysis
        env_analysis = summary.get('environment_analysis', {})
        env_dist = env_analysis.get('environment_distribution', {})
        if env_dist:
            print(f"🌍 ENVIRONMENT ANALYSIS:")
            for env, count in sorted(env_dist.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats.get('total_tests', 1)) * 100
                print(f"   - {env.capitalize()}: {count} tests ({percentage:.1f}%)")
            
            # Environment performance if available
            env_perf = env_analysis.get('environment_performance', {})
            if env_perf:
                print(f"\n   Environment Performance:")
                for env, perf_data in sorted(env_perf.items(), key=lambda x: x[1]['average_seconds']):
                    print(f"     {env.capitalize()}: {perf_data['average_seconds']:.1f}s avg")
            print()
        
        # Performance insights
        perf_analysis = enhanced_analysis.get('performance_analysis', {})
        if perf_analysis and 'error' not in perf_analysis:
            print(f"⚡ PERFORMANCE INSIGHTS:")
            print(f"   Average Duration: {perf_analysis.get('average_duration_seconds', 0):.1f} seconds")
            print(f"   Total Execution Time: {perf_analysis.get('total_execution_time_minutes', 0):.1f} minutes")
            
            perf_dist = perf_analysis.get('performance_percentages', {})
            print(f"   Fast Tests (<5s): {perf_dist.get('fast', 0):.1f}%")
            print(f"   Normal Tests (5-30s): {perf_dist.get('normal', 0):.1f}%")
            print(f"   Slow Tests (>30s): {perf_dist.get('slow', 0) + perf_dist.get('very_slow', 0):.1f}%")
            
            # Performance extremes
            perf_insights = perf_analysis.get('performance_insights', {})
            if perf_insights:
                fastest = perf_insights.get('fastest_test', {})
                slowest = perf_insights.get('slowest_test', {})
                print(f"\n   Fastest Test: {fastest.get('duration_seconds', 0):.2f}s")
                print(f"   Slowest Test: {slowest.get('duration_seconds', 0):.2f}s")
            print()
        
        # Top actionable insights
        failure_insights = summary.get('failure_insights', {})
        top_hints = failure_insights.get('top_failure_hints', [])
        if top_hints:
            print(f"💡 TOP ACTIONABLE INSIGHTS:")
            for i, hint_data in enumerate(top_hints[:3], 1):
                print(f"   {i}. {hint_data['test_name']} ({hint_data['category']}):")
                print(f"      {hint_data['hint']}")
            print()
        
        # Critical issues
        critical_issues = failure_insights.get('critical_issues', [])
        if critical_issues:
            print(f"🚨 CRITICAL ISSUES ({len(critical_issues)}):")
            for issue in critical_issues[:2]:
                print(f"   - {issue['test_name']}: {issue['hint']}")
            print()
        
        print("="*80)
    
    def generate_reports(self, analysis, results):
        """Generate detailed reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_files = []
        
        try:
            # CSV Report
            csv_file = self.output_dir / f"local_analysis_{timestamp}.csv"
            self.batch_analyzer.generate_csv_report(results, str(csv_file))
            report_files.append(csv_file)
            
            # HTML Report
            html_file = self.output_dir / f"local_report_{timestamp}.html"
            self.batch_analyzer.generate_html_report(analysis, results, str(html_file))
            report_files.append(html_file)
            
            # Executive Summary
            summary_file = self.output_dir / f"executive_summary_{timestamp}.md"
            self.generate_executive_summary(analysis, str(summary_file))
            report_files.append(summary_file)
            
            # JSON Export (for integration)
            json_file = self.output_dir / f"analysis_data_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump({
                    'analysis': analysis,
                    'timestamp': timestamp,
                    'source_directory': str(self.input_dir),
                    'total_files_processed': len(results)
                }, f, indent=2, default=str)
            report_files.append(json_file)
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            print(f"⚠️  Report generation partially failed: {e}")
        
        return report_files
    
    def generate_enhanced_reports(self, enhanced_analysis):
        """Generate enhanced reports with all new features"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_files = []
        
        try:
            # Save enhanced analysis using integrated analyzer
            enhanced_output_dir = self.output_dir / "enhanced"
            saved_files = self.integrated_analyzer.save_enhanced_results(
                enhanced_analysis, 
                str(enhanced_output_dir)
            )
            
            # Add all generated files to report list
            for file_type, file_path in saved_files.items():
                report_files.append(file_path)
            
            # Generate comprehensive enhanced report
            enhanced_report = self.integrated_analyzer.generate_enhanced_report(enhanced_analysis)
            comprehensive_file = self.output_dir / f"comprehensive_enhanced_report_{timestamp}.md"
            with open(comprehensive_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_report)
            report_files.append(str(comprehensive_file))
            
            # Generate actionable insights summary
            insights_file = self.output_dir / f"actionable_insights_{timestamp}.md"
            self.generate_actionable_insights_report(enhanced_analysis, str(insights_file))
            report_files.append(str(insights_file))
            
        except Exception as e:
            self.logger.error(f"Enhanced report generation failed: {e}")
            print(f"⚠️  Enhanced report generation partially failed: {e}")
        
        return report_files
    
    def generate_actionable_insights_report(self, enhanced_analysis, output_file):
        """Generate a focused report on actionable insights"""
        summary = enhanced_analysis.get('summary', {})
        failure_insights = summary.get('failure_insights', {})
        improvements = enhanced_analysis.get('improvements', {})
        
        content = f"""# 🎯 Actionable Insights Report

## Executive Summary
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source Directory**: {self.input_dir}
- **Enhancement Impact**: {improvements.get('categorization_improvement', {}).get('improvement_count', 0)} unknown categories resolved

## 🚨 Critical Actions Needed

"""
        
        # Critical issues
        critical_issues = failure_insights.get('critical_issues', [])
        if critical_issues:
            content += "### Immediate Attention Required:\n"
            for i, issue in enumerate(critical_issues, 1):
                content += f"{i}. **{issue['test_name']}** ({issue['environment']})\n"
                content += f"   - Issue: {issue['hint']}\n"
                content += f"   - Category: {issue['category']}\n\n"
        else:
            content += "✅ No critical issues identified.\n\n"
        
        # Top actionable hints
        top_hints = failure_insights.get('top_failure_hints', [])
        if top_hints:
            content += "## 💡 Top Actionable Items\n\n"
            for i, hint in enumerate(top_hints[:10], 1):
                content += f"### {i}. {hint['test_name']}\n"
                content += f"- **Environment**: {hint['environment']}\n"
                content += f"- **Category**: {hint['category']}\n"
                content += f"- **Action**: {hint['hint']}\n\n"
        
        # Performance-related failures
        perf_failures = failure_insights.get('performance_related_failures', [])
        if perf_failures:
            content += "## 🐌 Performance Optimization Opportunities\n\n"
            for failure in perf_failures:
                content += f"- **{failure['test_name']}**: {failure['hint']}\n"
            content += "\n"
        
        # Categorization improvements
        cat_improvement = improvements.get('categorization_improvement', {})
        if cat_improvement.get('improvement_count', 0) > 0:
            content += f"""## ✨ Enhanced Analysis Benefits

The enhanced analyzer successfully resolved **{cat_improvement.get('improvement_count', 0)} unknown categories**, providing {cat_improvement.get('improvement_percentage', 0):.1f}% improvement in categorization accuracy.

This means {cat_improvement.get('improvement_count', 0)} tests that were previously categorized as "unknown" now have specific, actionable categorizations.

"""
        
        # Performance insights
        perf_analysis = enhanced_analysis.get('performance_analysis', {})
        if perf_analysis and 'error' not in perf_analysis:
            perf_insights = perf_analysis.get('performance_insights', {})
            recommendations = perf_insights.get('recommendations', [])
            if recommendations:
                content += "## ⚡ Performance Recommendations\n\n"
                for i, rec in enumerate(recommendations, 1):
                    content += f"{i}. {rec}\n"
                content += "\n"
        
        content += f"""## 📋 Next Steps Checklist

### Immediate (Today)
- [ ] Review and address all critical issues listed above
- [ ] Investigate {len(top_hints[:3])} highest priority failures
- [ ] Check environment stability for failed tests

### Short Term (This Week)  
- [ ] Implement fixes for categorized failures
- [ ] Address performance optimization opportunities
- [ ] Schedule follow-up analysis after fixes

### Long Term (This Month)
- [ ] Establish monitoring for resolved issue categories
- [ ] Implement automated regression testing for fixed areas
- [ ] Document patterns and prevention strategies

---
*Generated by Enhanced Test Analyzer - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_executive_summary(self, analysis, output_file):
        """Generate executive summary report"""
        # Calculate pass rate
        pass_rate = 100 - analysis.get('failure_rate', 0)
        
        content = f"""# Test Analysis Executive Summary
        
## Overview
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source Directory**: {self.input_dir}
- **Total Tests**: {analysis['total_tests']}
- **Pass Rate**: {pass_rate:.1f}%
- **Failure Rate**: {analysis['failure_rate']:.1f}%

## Quality Status
- **Needs Attention**: {analysis.get('needs_attention', 0)} failures
- **Flaky Tests**: {analysis.get('flaky_tests', 0)} tests

## Failure Breakdown
"""
        
        if analysis.get('category_breakdown'):
            for category, count in analysis['category_breakdown'].items():
                percentage = (count / analysis['failed_tests'] * 100) if analysis['failed_tests'] > 0 else 0
                content += f"- **{category}**: {count} failures ({percentage:.1f}%)\n"
        
        content += f"""
## Recommendations
"""
        
        # Add recommendations based on analysis
        recommendations = self.generate_recommendations(analysis)
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"
        
        content += f"""
## Next Steps
1. Review high priority failures first
2. Address authentication and data issues immediately
3. Investigate timeout patterns
4. Schedule follow-up analysis after fixes

---
*Generated by Local Test Analyzer - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(output_file, 'w') as f:
            f.write(content)
    
    def generate_recommendations(self, analysis):
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        failure_breakdown = analysis.get('failure_breakdown', {})
        
        if failure_breakdown.get('Authentication Error', 0) > 0:
            recommendations.append("Review authentication service stability and token management")
        
        if failure_breakdown.get('Timeout', 0) > 2:
            recommendations.append("Investigate page load performance and increase timeout thresholds")
        
        if failure_breakdown.get('Network/API Error', 0) > 0:
            recommendations.append("Check API endpoint availability and network connectivity")
        
        if failure_breakdown.get('Data/State Issue', 0) > 1:
            recommendations.append("Review test data setup and application state management")
        
        if analysis.get('failure_rate', 0) > 15:
            recommendations.append("Failure rate exceeds threshold - consider environment stability review")
        
        if not recommendations:
            recommendations.append("Continue monitoring test execution patterns")
        
        return recommendations
    
    def send_notifications(self, analysis):
        """Send notifications if configured"""
        try:
            # Check if notification is configured
            if not os.path.exists('.env'):
                print("💡 Notifications skipped - .env file not found")
                return
            
            print("📧 Sending notifications...")
            
            # Create notification message
            message = f"""🔍 Local Test Analysis Complete
            
📊 **Summary**:
- Total Tests: {analysis['total_tests']}
- Pass Rate: {analysis['pass_rate']:.1f}%
- Failed Tests: {analysis['failed_tests']}
- High Priority Issues: {analysis.get('high_priority_count', 0)}

📁 **Source**: {self.input_dir}
📅 **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{"❌ Quality gates failed!" if not analysis.get('quality_gates_passed', True) else "✅ Quality gates passed"}
"""
            
            # Send via scheduler's notification system
            self.scheduler.send_slack_notification("Local Test Analysis", message)
            self.scheduler.send_email_notification(
                subject=f"Local Test Analysis - {analysis['pass_rate']:.1f}% Pass Rate",
                content=message,
                is_html=False
            )
            
            print("✅ Notifications sent")
            
        except Exception as e:
            print("⚠️  Notification sending failed: {e}")

    def send_enhanced_notifications(self, enhanced_analysis):
        """Send enhanced notifications with detailed insights"""
        try:
            # Check if notification is configured
            if not os.path.exists('.env'):
                print("💡 Notifications skipped - .env file not found")
                return
            
            print("📧 Sending enhanced notifications...")
            
            summary = enhanced_analysis.get('summary', {})
            stats = summary.get('test_statistics', {})
            improvements = enhanced_analysis.get('improvements', {})
            failure_insights = summary.get('failure_insights', {})
            
            # Create enhanced notification message
            message = f"""🚀 Enhanced Test Analysis Complete
            
📊 **Execution Summary**:
- Total Tests: {stats.get('total_tests', 0)}
- Pass Rate: {stats.get('pass_rate_percentage', 0):.1f}%
- Failed Tests: {stats.get('failed_tests', 0)}

✨ **Enhanced Analysis Impact**:
- Unknown Categories Resolved: {improvements.get('categorization_improvement', {}).get('improvement_count', 0)}
- Categorization Improvement: {improvements.get('categorization_improvement', {}).get('improvement_percentage', 0):.1f}%
- Actionable Hints Generated: {summary.get('enhanced_categorization', {}).get('actionable_hints_generated', 0)}

🚨 **Critical Issues**: {len(failure_insights.get('critical_issues', []))}
⚡ **Performance Issues**: {len(failure_insights.get('performance_related_failures', []))}

📁 **Source**: {self.input_dir}
📅 **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{self._get_quality_status_message(stats)}
"""
            
            # Send via scheduler's notification system
            if self.scheduler:
                self.scheduler.send_slack_notification("Enhanced Test Analysis", message)
                self.scheduler.send_email_notification(
                    subject=f"Enhanced Test Analysis - {stats.get('pass_rate_percentage', 0):.1f}% Pass Rate",
                    content=message,
                    is_html=False
                )
            
            print("✅ Enhanced notifications sent")
            
        except Exception as e:
            print(f"⚠️  Enhanced notification sending failed: {e}")
    
    def _get_quality_status_message(self, stats):
        """Generate quality status message based on metrics"""
        pass_rate = stats.get('pass_rate_percentage', 0)
        
        if pass_rate >= 95:
            return "🟢 Excellent quality - All systems green!"
        elif pass_rate >= 85:
            return "🟡 Good quality - Minor issues to address"
        elif pass_rate >= 70:
            return "🟠 Quality concerns - Review needed"
        else:
            return "🔴 Quality gates failed - Immediate action required!"
    
    def generate_basic_analysis(self, results):
        """Fallback method for basic analysis if enhanced analysis fails"""
        total_tests = len(results)
        failed_tests = sum(1 for test in results if test.get('status') == 'failed')
        passed_tests = total_tests - failed_tests
        
        return {
            'total_tests': total_tests,
            'failed_tests': failed_tests,
            'passed_tests': passed_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'failure_rate': (failed_tests / total_tests * 100) if total_tests > 0 else 0,
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
  
  # Quick analysis (basic categorization only)
  python local_analyzer.py --input "C:\\test-results" --quick
  
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
        help='Output directory for reports (default: ./local_reports)'
    )
    
    parser.add_argument(
        '--notify', '-n',
        action='store_true',
        help='Send notifications (requires .env configuration)'
    )
    
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Quick analysis only (basic categorization, no enhanced features)'
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
            generate_reports=not args.quick
        )
        
        if result:
            print(f"\n✅ Analysis completed successfully!")
            if not args.quick:
                print(f"📊 Reports saved to: {analyzer.output_dir}")
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