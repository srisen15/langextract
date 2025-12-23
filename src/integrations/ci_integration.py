#!/usr/bin/env python3
"""
CI/CD Integration Script for Test Log Analysis
This script can be integrated into your CI/CD pipeline to automatically analyze test results
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def main():
    """Main CI/CD integration function"""

    # Configuration - can be set via environment variables
    test_results_dir = os.environ.get('TEST_RESULTS_DIR', './test-results')
    max_failure_rate = float(os.environ.get('MAX_FAILURE_RATE', '10.0'))  # 10%
    max_critical_failures = int(os.environ.get('MAX_CRITICAL_FAILURES', '0'))
    max_high_priority = int(os.environ.get('MAX_HIGH_PRIORITY', '5'))

    print(f"🔍 Analyzing test results in: {test_results_dir}")

    # Check if test results directory exists
    if not os.path.exists(test_results_dir):
        print(f"❌ Test results directory not found: {test_results_dir}")
        return 0  # Don't fail if no test results

    # Run the analyzer with CSV output only (faster for CI)
    try:
        result = subprocess.run([
            'python', 'production_analyzer.py',
            '--directory', test_results_dir,
            '--output-format', 'csv',
            '--quiet'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))

        if result.returncode != 0:
            print(f"❌ Analyzer failed: {result.stderr}")
            return 1

    except FileNotFoundError:
        print("❌ production_analyzer.py not found. Make sure it's in the same directory.")
        return 1

    # Find the generated CSV file
    csv_files = list(Path(test_results_dir).glob('test_analysis_*.csv'))
    if not csv_files:
        print("❌ No analysis results found")
        return 1

    latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)

    # Analyze the results
    analysis_results = analyze_csv_results(latest_csv)

    # Print summary
    print_ci_summary(analysis_results)

    # Determine if build should fail
    exit_code = determine_build_status(
        analysis_results,
        max_failure_rate,
        max_critical_failures,
        max_high_priority
    )

    # Generate build annotations (for GitHub Actions, etc.)
    generate_build_annotations(analysis_results)

    return exit_code


def analyze_csv_results(csv_file):
    """Analyze the CSV results and extract key metrics"""
    import csv

    results = {
        'total_tests': 0,
        'failed_tests': 0,
        'passed_tests': 0,
        'critical_failures': 0,
        'high_priority_failures': 0,
        'needs_attention': 0,
        'flaky_tests': 0,
        'categories': {},
        'failure_details': []
    }

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            results['total_tests'] += 1

            if row['status'] == 'failed':
                results['failed_tests'] += 1

                # Count by priority
                if row['priority'] == 'Critical':
                    results['critical_failures'] += 1
                elif row['priority'] == 'High':
                    results['high_priority_failures'] += 1

                # Count categories
                category = row['failure_category']
                results['categories'][category] = results['categories'].get(category, 0) + 1

                # Needs attention
                if row['needs_attention'] == 'True':
                    results['needs_attention'] += 1

                # Store failure details
                results['failure_details'].append({
                    'name': row['test_name'],
                    'category': row['failure_category'],
                    'priority': row['priority'],
                    'error': row['failure_reason'][:100] + '...' if len(row['failure_reason']) > 100 else row['failure_reason']
                })
            else:
                results['passed_tests'] += 1

            # Flaky tests
            if row['is_flaky'] == 'True':
                results['flaky_tests'] += 1

    # Calculate failure rate
    results['failure_rate'] = (
        results['failed_tests'] /
        results['total_tests'] *
        100) if results['total_tests'] > 0 else 0

    return results


def print_ci_summary(results):
    """Print a CI-friendly summary"""
    print(f"""
📊 TEST ANALYSIS SUMMARY
========================
Total Tests: {results['total_tests']}
Passed: {results['passed_tests']} ✅
Failed: {results['failed_tests']} ❌
Failure Rate: {results['failure_rate']:.1f}%

🚨 Priority Breakdown:
- Critical: {results['critical_failures']}
- High Priority: {results['high_priority_failures']}
- Need Attention: {results['needs_attention']}
- Flaky Tests: {results['flaky_tests']}
""")

    if results['categories']:
        print("📋 Failure Categories:")
        for category, count in sorted(results['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {category}: {count}")

    if results['failure_details']:
        print(f"\n🔍 Top Failures:")
        for detail in results['failure_details'][:3]:  # Show top 3
            print(f"  - {detail['name']} [{detail['priority']}]")
            print(f"    Category: {detail['category']}")
            print(f"    Error: {detail['error']}")


def determine_build_status(results, max_failure_rate, max_critical_failures, max_high_priority):
    """Determine if the build should pass or fail"""
    reasons = []

    # Check failure rate
    if results['failure_rate'] > max_failure_rate:
        reasons.append(f"Failure rate ({results['failure_rate']:.1f}%) exceeds threshold ({max_failure_rate}%)")

    # Check critical failures
    if results['critical_failures'] > max_critical_failures:
        reasons.append(f"Critical failures ({results['critical_failures']}) exceed threshold ({max_critical_failures})")

    # Check high priority failures
    if results['high_priority_failures'] > max_high_priority:
        reasons.append(
            f"High priority failures ({
                results['high_priority_failures']}) exceed threshold ({max_high_priority})")

    if reasons:
        print(f"\n❌ BUILD FAILED - Quality Gates Not Met:")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    else:
        print(f"\n✅ BUILD PASSED - All quality gates met")
        return 0


def generate_build_annotations(results):
    """Generate annotations for CI systems"""

    # GitHub Actions annotations
    if os.environ.get('GITHUB_ACTIONS'):
        if results['critical_failures'] > 0:
            print(f"::error::Found {results['critical_failures']} critical test failures")

        if results['high_priority_failures'] > 0:
            print(f"::warning::Found {results['high_priority_failures']} high priority test failures")

        if results['flaky_tests'] > 0:
            print(f"::notice::Found {results['flaky_tests']} flaky tests that should be investigated")

    # Azure DevOps format
    elif os.environ.get('AZURE_DEVOPS'):
        if results['critical_failures'] > 0:
            print(f"##vso[task.logissue type=error]Found {results['critical_failures']} critical test failures")

        if results['high_priority_failures'] > 0:
            print(
                f"##vso[task.logissue type=warning]Found {
                    results['high_priority_failures']} high priority test failures")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
