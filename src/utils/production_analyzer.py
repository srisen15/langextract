#!/usr/bin/env python3
"""
Production Test Log Analyzer
Command-line tool for analyzing Playwright test execution logs in batch
"""

import argparse
import sys
import os
from pathlib import Path
from test_log_analyzer import BatchTestAnalyzer, TestLogExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Playwright test execution logs and categorize failures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all JSON files in a directory
  python production_analyzer.py --directory ./test-results

  # Analyze single file
  python production_analyzer.py --file test-result.json

  # Generate only CSV report
  python production_analyzer.py --directory ./logs --output-format csv

  # Filter high priority only
  python production_analyzer.py --directory ./logs --priority-filter high
        """
    )

    # Input options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--directory', '-d',
                       help='Directory containing test log files')
    group.add_argument('--file', '-f',
                       help='Single test log file to analyze')

    # Output options
    parser.add_argument('--output-dir', '-o',
                        help='Output directory for reports (default: same as input)')
    parser.add_argument('--output-format',
                        choices=['all', 'csv', 'html', 'markdown'],
                        default='all',
                        help='Output format (default: all)')

    # Filtering options
    parser.add_argument('--priority-filter',
                        choices=['critical', 'high', 'medium', 'low', 'all'],
                        default='all',
                        help='Filter by priority level')
    parser.add_argument('--category-filter',
                        help='Filter by failure category (comma-separated)')
    parser.add_argument('--needs-attention-only',
                        action='store_true',
                        help='Show only tests that need attention')

    # Pattern matching
    parser.add_argument('--pattern',
                        default='*.json',
                        help='File pattern to match (default: *.json)')

    # Reporting options
    parser.add_argument('--quiet', '-q',
                        action='store_true',
                        help='Suppress console output')
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    try:
        if args.file:
            # Single file analysis
            analyze_single_file(args)
        else:
            # Batch analysis
            analyze_directory(args)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_single_file(args):
    """Analyze a single test log file"""
    if not os.path.exists(args.file):
        raise FileNotFoundError(f"File not found: {args.file}")

    if not args.quiet:
        print(f"Analyzing file: {args.file}")

    extractor = TestLogExtractor(args.file)
    summary = extractor.extract_basic_info()

    if not summary:
        print("No valid test data found in file")
        return

    # Apply filters
    if should_include_test(summary, args):
        if not args.quiet:
            print_test_summary(summary, args.verbose)

        # Generate reports if needed
        output_dir = args.output_dir or os.path.dirname(args.file)
        generate_single_file_reports(extractor, output_dir, args)


def analyze_directory(args):
    """Analyze all test log files in a directory"""
    if not os.path.exists(args.directory):
        raise FileNotFoundError(f"Directory not found: {args.directory}")

    analyzer = BatchTestAnalyzer(args.directory)
    results = analyzer.analyze_all_logs(args.pattern)

    if not results:
        print("No test log files found")
        return

    # Apply filters
    filtered_results = []
    for result in results:
        if should_include_test(result, args):
            filtered_results.append(result)

    if not args.quiet:
        print_batch_summary(filtered_results, analyzer, args.verbose)

    # Generate reports
    output_dir = args.output_dir or args.directory
    generate_batch_reports(analyzer, filtered_results, output_dir, args)


def should_include_test(summary, args):
    """Check if test should be included based on filters"""
    # Priority filter
    if args.priority_filter != 'all':
        if summary.priority.lower() != args.priority_filter.lower():
            return False

    # Category filter
    if args.category_filter:
        categories = [c.strip().lower() for c in args.category_filter.split(',')]
        if summary.failure_category.lower() not in categories:
            return False

    # Needs attention filter
    if args.needs_attention_only and not summary.needs_attention:
        return False

    return True


def print_test_summary(summary, verbose=False):
    """Print summary of a single test"""
    status_icon = "❌" if summary.status == 'failed' else "✅"
    attention_icon = "🚨" if summary.needs_attention else ""
    flaky_icon = "🔄" if summary.is_flaky else ""

    print(f"{status_icon} {attention_icon} {flaky_icon} {summary.test_name}")
    print(f"   Status: {summary.status}")
    print(f"   Category: {summary.failure_category}")
    print(f"   Priority: {summary.priority}")
    print(f"   Duration: {summary.duration_seconds:.2f}s")

    if verbose and summary.status == 'failed':
        print(f"   Error: {summary.failure_reason[:100]}...")
        print(f"   Location: {summary.error_location}")


def print_batch_summary(filtered_results, analyzer, verbose=False):
    """Print summary of batch analysis"""
    summary = analyzer.generate_failure_summary()

    print(f"""
📊 ANALYSIS SUMMARY
==================
Total Tests Analyzed: {summary['total_tests']}
Failed Tests: {summary['failed_tests']}
Failure Rate: {summary['failure_rate']:.1f}%
Tests Needing Attention: {summary['needs_attention']}
Flaky Tests: {summary['flaky_tests']}
Tests Matching Filters: {len(filtered_results)}
""")

    if verbose:
        print("\n📋 FAILURE CATEGORIES:")
        for category, count in summary['category_breakdown'].items():
            percentage = (count / summary['failed_tests'] * 100) if summary['failed_tests'] > 0 else 0
            print(f"  {category}: {count} ({percentage:.1f}%)")

        print("\n🎯 PRIORITY BREAKDOWN:")
        for priority, count in summary['priority_breakdown'].items():
            print(f"  {priority}: {count}")

    # Show high priority failures
    high_priority = [r for r in filtered_results if r.needs_attention and r.status == 'failed']
    if high_priority:
        print(f"\n🚨 HIGH PRIORITY FAILURES ({len(high_priority)} tests):")
        for test in high_priority[:5]:  # Show top 5
            print(f"  - {test.test_name} [{test.failure_category}] - {test.priority}")
        if len(high_priority) > 5:
            print(f"  ... and {len(high_priority) - 5} more")


def generate_single_file_reports(extractor, output_dir, args):
    """Generate reports for single file analysis"""
    base_name = Path(extractor.json_file_path).stem

    if args.output_format in ['all', 'markdown']:
        report_file = os.path.join(output_dir, f"{base_name}_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(extractor.generate_test_report())
        if not args.quiet:
            print(f"Generated: {report_file}")


def generate_batch_reports(analyzer, filtered_results, output_dir, args):
    """Generate reports for batch analysis"""
    # Update analyzer results with filtered results
    analyzer.results = filtered_results

    if args.output_format in ['all', 'csv']:
        csv_file = analyzer.export_to_csv()
        if not args.quiet:
            print(f"Generated: {csv_file}")

    if args.output_format in ['all', 'html']:
        html_file = analyzer.generate_html_report()
        if not args.quiet:
            print(f"Generated: {html_file}")

    if args.output_format in ['all', 'markdown']:
        insights = analyzer.generate_actionable_report()
        insights_file = os.path.join(output_dir, "actionable_insights.md")
        with open(insights_file, 'w', encoding='utf-8') as f:
            f.write(insights)
        if not args.quiet:
            print(f"Generated: {insights_file}")


if __name__ == "__main__":
    main()
