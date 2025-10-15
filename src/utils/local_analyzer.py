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

class LocalTestAnalyzer:
    """Enhanced local test log analyzer with all production features"""
    
    def __init__(self, input_dir, output_dir=None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else Path("./output/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize batch analyzer with input directory
        self.batch_analyzer = BatchTestAnalyzer(str(self.input_dir))
        
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
        Analyze local test files with full feature set
        
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
            
            # Analyze files
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
            
            # Generate comprehensive analysis using batch analyzer
            # Convert our results back to TestExecutionSummary objects for batch analysis
            test_summaries = []
            for result_dict in results:
                # Create a temporary file to initialize TestLogExtractor
                from core.test_log_analyzer import TestExecutionSummary
                summary = TestExecutionSummary(
                    test_name=result_dict['test_name'],
                    full_name=result_dict['full_name'],
                    status=result_dict['status'],
                    duration_ms=result_dict['duration_ms'],
                    duration_seconds=result_dict['duration_seconds'],
                    failure_reason=result_dict['failure_reason'],
                    error_location=result_dict['error_location'],
                    retries_count=result_dict['retries_count'],
                    test_file=result_dict['test_file'],
                    tags=result_dict['tags'],
                    failure_category=result_dict['failure_category'],
                    priority=result_dict['priority'],
                    is_flaky=result_dict['is_flaky'],
                    environment=result_dict['environment'],
                    needs_attention=result_dict['status'] == 'failed'  # Simple logic for needs attention
                )
                test_summaries.append(summary)
            
            # Set results in batch analyzer
            self.batch_analyzer.results = test_summaries
            analysis = self.batch_analyzer.generate_failure_summary()
            
            # Display summary
            self.display_summary(analysis)
            
            if generate_reports:
                # Generate reports
                report_files = self.generate_reports(analysis, results)
                print(f"\n📊 Reports generated:")
                for report_file in report_files:
                    print(f"   - {report_file}")
            
            if send_notifications:
                # Send notifications (if configured)
                self.send_notifications(analysis)
            
            return analysis
            
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
            print(f"⚠️  Notification sending failed: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Analyze test logs from local directory with enhanced features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python local_analyzer.py --input "C:\\test-results"
  
  # With notifications
  python local_analyzer.py --input "C:\\test-results" --notify
  
  # Custom output directory
  python local_analyzer.py --input "C:\\test-results" --output "C:\\reports"
  
  # Quick analysis (no detailed reports)
  python local_analyzer.py --input "C:\\test-results" --quick
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
        help='Quick analysis only (no detailed reports)'
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