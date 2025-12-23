#!/usr/bin/env python3
r"""
MAIN ENTRY POINT - Test Results Analyzer
============================================
Use this file to analyze your test results JSON files and generate reports.

USAGE:
    python analyze_tests.py --input "path/to/test/results"

EXAMPLES:
    # Basic analysis
    python analyze_tests.py --input "C:\Users\YourName\Downloads\test results"

    # With enhanced reports (includes 401/403 categorization)
    python analyze_tests.py --input "C:\Users\YourName\Downloads\test results" --enhanced

    # Specify output directory
    python analyze_tests.py --input "C:\test_results" --output "C:\reports"

    # Verbose mode
    python analyze_tests.py --input "C:\test_results" --enhanced --verbose
"""

from enhanced_analyzer import EnhancedLocalAnalyzer
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import yaml

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_utils_dir = os.path.join(current_dir, 'src', 'utils')
sys.path.insert(0, src_utils_dir)

# Import the enhanced analyzer directly

# Load configuration


def load_config():
    """Load configuration from config.yaml or return defaults"""
    # Look for config.yaml in docs/configuration folder first, then fall back to root
    config_paths = [
        Path(__file__).parent / 'docs' / 'configuration' / 'config.yaml',
        Path(__file__).parent / 'config.yaml'
    ]

    config_path = None
    for path in config_paths:
        if path.exists():
            config_path = path
            break

    # Default configuration
    default_config = {
        'quality_thresholds': {
            'good': 90,
            'acceptable': 75
        },
        'priority_thresholds': {
            'authentication_high': 5,
            'performance_medium': 5
        },
        'report_settings': {
            'max_categories_in_summary': 5,
            'max_environments_in_summary': 5,
            'include_recommendations': True,
            'include_environment_distribution': True
        }
    }

    try:
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                print(f"✅ Loaded configuration from {config_path.name}")
                return config if config else default_config
        else:
            print(f"⚠️  Config file not found, using default configuration")
    except Exception as e:
        print(f"⚠️  Warning: Could not load config.yaml ({e}), using defaults")

    return default_config


# Global config
CONFIG = load_config()


def find_json_files(input_dir):
    """Find all JSON test result files in the input directory"""
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"❌ Error: Directory not found: {input_dir}")
        return []

    json_files = list(input_path.glob("**/*.json"))

    if not json_files:
        print(f"⚠️  Warning: No JSON files found in {input_dir}")
        return []

    print(f"📁 Found {len(json_files)} JSON file(s) in {input_dir}")
    return json_files


def load_test_results(json_files):
    """Load test results from JSON files"""
    all_results = []

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Handle different JSON structures
                if isinstance(data, list):
                    all_results.extend(data)
                elif isinstance(data, dict):
                    # Check if it's a test result object
                    if 'tests' in data:
                        all_results.extend(data['tests'])
                    elif 'results' in data:
                        all_results.extend(data['results'])
                    elif 'status' in data and 'name' in data:
                        # Allure-format single test result - normalize it
                        normalized = {
                            'test_name': data.get('name', 'Unknown'),
                            'status': 'FAIL' if data['status'] in ['failed', 'broken'] else 'PASS',
                            'error_message': '',
                            'environment': 'unknown'
                        }

                        # Extract error message from multiple possible locations
                        # Priority: statusMessage, statusTrace, testStage.statusMessage
                        if data.get('statusMessage'):
                            normalized['error_message'] = data['statusMessage']
                        elif data.get('statusTrace'):
                            # Use first line of stack trace if no statusMessage
                            normalized['error_message'] = data['statusTrace'].split('\n')[0]
                        elif data.get('testStage', {}).get('statusMessage'):
                            normalized['error_message'] = data['testStage']['statusMessage']
                        elif data.get('statusDetails', {}).get('message'):
                            normalized['error_message'] = data['statusDetails']['message']

                        # Extract environment from labels
                        for label in data.get('labels', []):
                            if label.get('name') == 'host':
                                normalized['environment'] = label.get('value', 'unknown')
                                break
                            elif label.get('name') == 'env':
                                normalized['environment'] = label.get('value', 'unknown')
                                break

                        all_results.append(normalized)
                    else:
                        # Single test result (legacy format)
                        all_results.append(data)

        except json.JSONDecodeError as e:
            print(f"⚠️  Skipping invalid JSON file: {json_file.name} ({e})")
        except Exception as e:
            print(f"⚠️  Error reading {json_file.name}: {e}")

    return all_results


def get_quality_status(pass_rate, config=None):
    """Determine quality status based on pass rate and configuration thresholds"""
    if config is None:
        config = CONFIG

    thresholds = config.get('quality_thresholds', {})
    good_threshold = thresholds.get('good', 90)
    acceptable_threshold = thresholds.get('acceptable', 75)

    if pass_rate >= good_threshold:
        return 'GOOD', '🟢'
    elif pass_rate >= acceptable_threshold:
        return 'NEEDS ATTENTION', '🟡'
    else:
        return 'CRITICAL', '🔴'


def generate_executive_summary_html(analysis, output_dir):
    """Generate HTML executive summary for email"""
    html_path = output_dir / f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    summary = analysis.get('summary', {})
    failure_cats = analysis.get('failure_categories', {})
    env_dist = analysis.get('environment_distribution', {})

    # Calculate metrics
    total_tests = summary.get('total_tests', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    pass_rate = summary.get('pass_rate', 0)

    # Get quality status from config thresholds
    quality_text, quality_icon = get_quality_status(pass_rate)

    # Quality status with colors
    if quality_text == 'GOOD':
        quality_badge = f'<span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;">{quality_icon} {quality_text}</span>'
        status_color = '#28a745'
    elif quality_text == 'NEEDS ATTENTION':
        quality_badge = f'<span style="background-color: #ffc107; color: black; padding: 4px 12px; border-radius: 4px; font-weight: bold;">{quality_icon} {quality_text}</span>'
        status_color = '#ffc107'
    else:  # CRITICAL
        quality_badge = f'<span style="background-color: #dc3545; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;">{quality_icon} {quality_text}</span>'
        status_color = '#dc3545'

    # Top issues
    auth_failures = failure_cats.get('authentication_failure', 0) + failure_cats.get('authorization_failure', 0)
    perf_issues = failure_cats.get('performance_issue', 0) + failure_cats.get('connectivity_issue', 0)
    ui_issues = failure_cats.get('ui_interaction_failure', 0)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Analysis Executive Summary</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 12px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-card.success {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }}
        .metric-card.warning {{
            background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
        }}
        .metric-card.danger {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .priority-card {{
            border-left: 4px solid #dc3545;
            background-color: #fff5f5;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .priority-card.medium {{
            border-left-color: #ffc107;
            background-color: #fffbf0;
        }}
        .priority-card h3 {{
            margin-top: 0;
            color: #dc3545;
        }}
        .priority-card.medium h3 {{
            color: #856404;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-high {{
            background-color: #dc3545;
            color: white;
        }}
        .badge-medium {{
            background-color: #ffc107;
            color: black;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Test Analysis Executive Summary</h1>

        <p style="color: #666; font-size: 14px;">
            <strong>Analysis Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br>
            <strong>Quality Status:</strong> {quality_badge}
        </p>

        <h2>📈 Key Metrics</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value">{total_tests}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Passed</div>
                <div class="metric-value">{passed}</div>
            </div>
            <div class="metric-card danger">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{failed}</div>
            </div>
            <div class="metric-card {'success' if pass_rate >= 90 else 'warning' if pass_rate >= 75 else 'danger'}">
                <div class="metric-label">Pass Rate</div>
                <div class="metric-value">{pass_rate:.1f}%</div>
            </div>
        </div>
"""

    # Top Failure Categories
    if failure_cats:
        sorted_cats = sorted(failure_cats.items(), key=lambda x: x[1], reverse=True)
        html_content += """
        <h2>🔍 Top Failure Categories</h2>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Count</th>
                    <th>% of Failures</th>
                </tr>
            </thead>
            <tbody>
"""
        for category, count in sorted_cats[:5]:
            percentage = (count / failed * 100) if failed > 0 else 0
            cat_name = category.replace('_', ' ').title()
            html_content += f"""
                <tr>
                    <td><strong>{cat_name}</strong></td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
"""
        html_content += """
            </tbody>
        </table>
"""

    # Priority Recommendations
    html_content += """
        <h2>🎯 Priority Recommendations</h2>
"""

    if auth_failures > 0:
        html_content += f"""
        <div class="priority-card">
            <h3><span class="badge badge-high">HIGH PRIORITY</span> Authentication/Authorization ({auth_failures} issues)</h3>
            <p><strong>Action Required:</strong> Review user management, token handling, and access control systems. Check OKTA/authentication service stability and investigate JWT token validation issues.</p>
        </div>
"""

    if perf_issues > 0:
        html_content += f"""
        <div class="priority-card medium">
            <h3><span class="badge badge-medium">MEDIUM PRIORITY</span> Performance/Connectivity ({perf_issues} issues)</h3>
            <p><strong>Action Required:</strong> Optimize infrastructure, review network configurations, and investigate timeout patterns. Check API response times and network latency.</p>
        </div>
"""

    if ui_issues > 0:
        html_content += f"""
        <div class="priority-card medium">
            <h3><span class="badge badge-medium">MEDIUM PRIORITY</span> UI Interactions ({ui_issues} issues)</h3>
            <p><strong>Action Required:</strong> Review element selectors, page load timing, and dynamic content handling. Verify element visibility and clickability conditions.</p>
        </div>
"""

    # Check if pass rate is below acceptable threshold (from config)
    acceptable_threshold = CONFIG.get('quality_thresholds', {}).get('acceptable', 75)
    if pass_rate < acceptable_threshold:
        html_content += f"""
        <div class="priority-card">
            <h3><span class="badge badge-high">HIGH PRIORITY</span> Overall Quality Alert</h3>
            <p><strong>Action Required:</strong> Pass rate ({pass_rate:.1f}%) is below acceptable threshold ({acceptable_threshold}%). Conduct comprehensive environment and application stability review.</p>
        </div>
"""

    # Next Steps
    html_content += """
        <h2>📋 Recommended Next Steps</h2>
        <ol>
            <li><strong>Immediate Action:</strong> Address HIGH priority authentication failures - investigate token management and service stability</li>
            <li><strong>Performance Review:</strong> Analyze timeout patterns and optimize infrastructure where needed</li>
            <li><strong>Root Cause Analysis:</strong> Deep dive into top failure categories to identify systemic issues</li>
            <li><strong>Follow-up Testing:</strong> Re-run tests after fixes are deployed to validate improvements</li>
            <li><strong>Trend Monitoring:</strong> Track failure categories over time for early issue detection</li>
        </ol>
"""

    # Environment Distribution (if available)
    if env_dist:
        sorted_envs = sorted(env_dist.items(), key=lambda x: x[1], reverse=True)
        html_content += """
        <h2>🌍 Test Distribution by Environment</h2>
        <table>
            <thead>
                <tr>
                    <th>Environment</th>
                    <th>Test Count</th>
                </tr>
            </thead>
            <tbody>
"""
        for env, count in sorted_envs[:5]:
            html_content += f"""
                <tr>
                    <td>{env}</td>
                    <td>{count}</td>
                </tr>
"""
        html_content += """
            </tbody>
        </table>
"""

    # Footer
    html_content += f"""
        <div class="footer">
            <p>Generated by Test Results Analyzer | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>📂 For detailed analysis, see the accompanying JSON and text reports</p>
        </div>
    </div>
</body>
</html>
"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return html_path


def generate_executive_summary_email(analysis, output_dir):
    """Generate plain text email-friendly summary"""
    email_path = output_dir / f"executive_summary_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    summary = analysis.get('summary', {})
    failure_cats = analysis.get('failure_categories', {})

    total_tests = summary.get('total_tests', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    pass_rate = summary.get('pass_rate', 0)

    # Get quality status from config thresholds
    quality_text, quality_icon = get_quality_status(pass_rate)

    auth_failures = failure_cats.get('authentication_failure', 0) + failure_cats.get('authorization_failure', 0)
    perf_issues = failure_cats.get('performance_issue', 0) + failure_cats.get('connectivity_issue', 0)

    email_content = f"""
================================================================================
TEST ANALYSIS EXECUTIVE SUMMARY
================================================================================

Analysis Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Quality Status: {quality_text}

--------------------------------------------------------------------------------
KEY METRICS
--------------------------------------------------------------------------------
Total Tests:    {total_tests}
Passed:         {passed}
Failed:         {failed}
Pass Rate:      {pass_rate:.1f}%

--------------------------------------------------------------------------------
TOP ISSUES
--------------------------------------------------------------------------------
"""

    if failure_cats:
        sorted_cats = sorted(failure_cats.items(), key=lambda x: x[1], reverse=True)
        for i, (category, count) in enumerate(sorted_cats[:5], 1):
            percentage = (count / failed * 100) if failed > 0 else 0
            cat_name = category.replace('_', ' ').title()
            email_content += f"{i}. {cat_name}: {count} failures ({percentage:.1f}%)\n"

    email_content += f"""
--------------------------------------------------------------------------------
PRIORITY RECOMMENDATIONS
--------------------------------------------------------------------------------
"""

    if auth_failures > 0:
        email_content += f"""
[HIGH PRIORITY] Authentication/Authorization ({auth_failures} issues)
→ Review user management, token handling, and access control systems
→ Check OKTA/authentication service stability
→ Investigate JWT token validation issues

"""

    if perf_issues > 0:
        email_content += f"""
[MEDIUM PRIORITY] Performance/Connectivity ({perf_issues} issues)
→ Optimize infrastructure and review network configurations
→ Investigate timeout patterns and API response times
→ Check network latency and service availability

"""

    # Check if pass rate is below acceptable threshold (from config)
    acceptable_threshold = CONFIG.get('quality_thresholds', {}).get('acceptable', 75)
    if pass_rate < acceptable_threshold:
        email_content += f"""
[HIGH PRIORITY] Overall Quality Alert
→ Pass rate ({pass_rate:.1f}%) is below acceptable threshold ({acceptable_threshold}%)
→ Conduct comprehensive environment and application stability review
→ Consider immediate remediation actions

"""

    email_content += f"""
--------------------------------------------------------------------------------
RECOMMENDED NEXT STEPS
--------------------------------------------------------------------------------
1. IMMEDIATE: Address HIGH priority authentication failures
2. PERFORMANCE: Analyze timeout patterns and optimize infrastructure
3. ROOT CAUSE: Deep dive into top failure categories
4. FOLLOW-UP: Re-run tests after fixes are deployed
5. MONITORING: Track failure trends over time

--------------------------------------------------------------------------------
For detailed analysis, please review the accompanying HTML report or contact
the QA team for assistance.

Generated by Test Results Analyzer | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================
"""

    with open(email_path, 'w', encoding='utf-8') as f:
        f.write(email_content)

    return email_path


def generate_executive_summary(analysis, output_dir):
    """Generate executive summary report for stakeholders (Markdown format)"""
    summary_path = output_dir / f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    summary = analysis.get('summary', {})
    failure_cats = analysis.get('failure_categories', {})
    env_dist = analysis.get('environment_distribution', {})

    # Calculate metrics
    total_tests = summary.get('total_tests', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    pass_rate = summary.get('pass_rate', 0)

    # Get quality status from config thresholds
    quality_text, quality_icon = get_quality_status(pass_rate)
    quality_status = f"{quality_icon} {quality_text}"

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Test Analysis Executive Summary\n\n")

        # Overview Section
        f.write("## 📊 Overview\n\n")
        f.write(f"- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Total Tests Analyzed**: {total_tests}\n")
        f.write(f"- **Tests Passed**: {passed}\n")
        f.write(f"- **Tests Failed**: {failed}\n")
        f.write(f"- **Pass Rate**: {pass_rate:.1f}%\n")
        f.write(f"- **Quality Status**: {quality_status}\n\n")

        # Key Findings
        f.write("## 🔍 Key Findings\n\n")

        if failure_cats:
            # Sort by count, descending
            sorted_cats = sorted(failure_cats.items(), key=lambda x: x[1], reverse=True)
            top_issues = sorted_cats[:3]

            f.write("### Top Failure Categories:\n\n")
            for i, (category, count) in enumerate(top_issues, 1):
                percentage = (count / failed * 100) if failed > 0 else 0
                cat_name = category.replace('_', ' ').title()
                f.write(f"{i}. **{cat_name}**: {count} occurrences ({percentage:.1f}% of failures)\n")
            f.write("\n")

        # Environment Analysis
        if env_dist:
            f.write("### Environment Distribution:\n\n")
            sorted_envs = sorted(env_dist.items(), key=lambda x: x[1], reverse=True)
            for env, count in sorted_envs[:5]:  # Top 5 environments
                f.write(f"- **{env}**: {count} tests\n")
            f.write("\n")

        # Priority Recommendations
        f.write("## 🎯 Priority Recommendations\n\n")

        auth_failures = failure_cats.get('authentication_failure', 0) + failure_cats.get('authorization_failure', 0)
        perf_issues = failure_cats.get('performance_issue', 0) + failure_cats.get('connectivity_issue', 0)
        ui_issues = failure_cats.get('ui_interaction_failure', 0)
        data_issues = failure_cats.get('data_validation_failure', 0)

        recommendations = []

        if auth_failures > 0:
            recommendations.append({
                'priority': '🔴 HIGH',
                'area': 'Authentication/Authorization',
                'count': auth_failures,
                'action': 'Review user management, token handling, and access control systems. Check OKTA/authentication service stability.'
            })

        if perf_issues > 0:
            recommendations.append({
                'priority': '🟡 MEDIUM',
                'area': 'Performance/Connectivity',
                'count': perf_issues,
                'action': 'Optimize infrastructure, review network configurations, and investigate timeout patterns.'
            })

        if ui_issues > 0:
            recommendations.append({
                'priority': '🟡 MEDIUM',
                'area': 'UI Interactions',
                'count': ui_issues,
                'action': 'Review element selectors, page load timing, and dynamic content handling.'
            })

        if data_issues > 0:
            recommendations.append({
                'priority': '🟡 MEDIUM',
                'area': 'Data Validation',
                'count': data_issues,
                'action': 'Review test data setup, expected values, and data transformation logic.'
            })

        # Check if pass rate is below acceptable threshold (from config)
        acceptable_threshold = CONFIG.get('quality_thresholds', {}).get('acceptable', 75)
        if pass_rate < acceptable_threshold:
            recommendations.append(
                {
                    'priority': '🔴 HIGH',
                    'area': 'Overall Quality',
                    'count': failed,
                    'action': f'Pass rate ({
                        pass_rate:.1f}%) below acceptable threshold ({acceptable_threshold}%) - conduct comprehensive environment and application stability review.'})

        if recommendations:
            for rec in recommendations:
                f.write(f"### {rec['priority']} - {rec['area']} ({rec['count']} issues)\n\n")
                f.write(f"**Action Required**: {rec['action']}\n\n")
        else:
            f.write("✅ No critical issues identified. Continue monitoring test execution patterns.\n\n")

        # Next Steps
        f.write("## 📋 Next Steps\n\n")
        f.write("1. **Review high priority failures first** - Focus on authentication and performance issues\n")
        f.write("2. **Address authentication issues immediately** - Investigate token management and service stability\n")
        f.write("3. **Investigate performance patterns** - Identify and resolve timeout root causes\n")
        f.write("4. **Schedule follow-up analysis** - Re-run tests after fixes are deployed\n")
        f.write("5. **Monitor trends** - Track failure categories over time for early detection\n\n")

        # Quality Metrics
        f.write("## 📈 Quality Metrics\n\n")
        f.write(f"- **Pass Rate**: {pass_rate:.1f}% ")
        if pass_rate >= 90:
            f.write("✅ Excellent\n")
        elif pass_rate >= 75:
            f.write("⚠️ Acceptable\n")
        else:
            f.write("❌ Needs Improvement\n")

        f.write(f"- **Failure Rate**: {100 - pass_rate:.1f}%\n")
        f.write(f"- **Categorized Failures**: {sum(failure_cats.values())} / {failed}\n")
        f.write(f"- **Test Coverage**: {total_tests} test cases executed\n\n")

        # Footer
        f.write("---\n\n")
        f.write(f"*Generated by Test Results Analyzer - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        f.write(f"\n📂 **Detailed Reports**: See `test_analysis_report_*.txt` and `failure_analysis_*.json` for complete details\n")

    return summary_path


def generate_text_report(analysis, output_dir):
    """Generate a human-readable text report"""
    report_path = output_dir / f"test_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("TEST ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")

        # Summary
        summary = analysis.get('summary', {})
        f.write("📊 SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Tests:  {summary.get('total_tests', 0)}\n")
        f.write(f"Passed:       {summary.get('passed', 0)}\n")
        f.write(f"Failed:       {summary.get('failed', 0)}\n")
        f.write(f"Pass Rate:    {summary.get('pass_rate', 0):.2f}%\n\n")

        # Environment Distribution
        env_dist = analysis.get('environment_distribution', {})
        if env_dist:
            f.write("🌍 ENVIRONMENT DISTRIBUTION\n")
            f.write("-" * 80 + "\n")
            for env, count in sorted(env_dist.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {env}: {count}\n")
            f.write("\n")

        # Failure Categories
        failure_cats = analysis.get('failure_categories', {})
        if failure_cats:
            f.write("🏷️  FAILURE CATEGORIES\n")
            f.write("-" * 80 + "\n")
            for category, count in sorted(failure_cats.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {category.replace('_', ' ').title()}: {count}\n")
            f.write("\n")

        # Detailed Failures
        enhanced_results = analysis.get('enhanced_results', [])
        failed_tests = [r for r in enhanced_results if r.get('status') == 'FAIL']

        if failed_tests:
            f.write("❌ DETAILED FAILURE ANALYSIS\n")
            f.write("=" * 80 + "\n\n")

            for i, test in enumerate(failed_tests, 1):
                f.write(f"[{i}] {test.get('test_name', 'Unknown Test')}\n")
                f.write(f"    Environment: {test.get('environment', 'Unknown')}\n")

                if test.get('failure_category'):
                    f.write(f"    Category: {test['failure_category'].replace('_', ' ').title()}\n")
                    f.write(f"    Confidence: {test.get('failure_confidence', 0):.0%}\n")
                    f.write(f"    💡 Hint: {test.get('failure_hint', 'N/A')}\n")

                if test.get('http_status_code'):
                    f.write(f"    🌐 HTTP Status: {test['http_status_code']}\n")

                f.write(f"    Error: {test.get('error_message', 'No error message')}\n")
                f.write("\n")

        f.write("=" * 80 + "\n")
        f.write(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    return report_path


def generate_json_report(analysis, output_dir):
    """Generate a JSON report"""
    report_path = output_dir / f"test_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)

    return report_path


def main():
    """Main entry point for test analysis"""
    parser = argparse.ArgumentParser(
        description='Analyze test results JSON files and generate comprehensive reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_tests.py --input "C:\\test_results"
  python analyze_tests.py --input "C:\\test_results" --enhanced
  python analyze_tests.py --input "C:\\test_results" --output "C:\\reports" --verbose
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input directory containing test result JSON files'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output directory for reports (default: ./output/reports)'
    )

    parser.add_argument(
        '--enhanced',
        action='store_true',
        help='Generate enhanced reports with 401/403 categorization and detailed analytics'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress information'
    )

    args = parser.parse_args()

    # Setup output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path('./output/reports')

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n🎯 Test Results Analyzer")
    print("=" * 60)

    # Find JSON files
    json_files = find_json_files(args.input)
    if not json_files:
        return

    # Load test results
    print("📖 Loading test results...")
    test_results = load_test_results(json_files)

    if not test_results:
        print("❌ No valid test results found in JSON files")
        return

    print(f"✅ Loaded {len(test_results)} test result(s)")

    # Analyze results
    print("\n🔍 Analyzing test results...")
    analyzer = EnhancedLocalAnalyzer()
    analysis = analyzer.analyze_batch_results(test_results)

    # Display summary
    print("\n📊 Analysis Summary:")
    print("-" * 60)
    summary = analysis.get('summary', {})
    print(f"  Total Tests: {summary.get('total_tests', 0)}")
    print(f"  Passed: {summary.get('passed', 0)}")
    print(f"  Failed: {summary.get('failed', 0)}")
    print(f"  Pass Rate: {summary.get('pass_rate', 0):.2f}%")

    # Show failure categories if enhanced mode
    if args.enhanced or analysis.get('failure_categories'):
        failure_cats = analysis.get('failure_categories', {})
        if failure_cats:
            print("\n🏷️  Failure Categories:")
            for category, count in sorted(failure_cats.items(), key=lambda x: x[1], reverse=True):
                print(f"    • {category.replace('_', ' ').title()}: {count}")

    # Generate reports
    print("\n📝 Generating reports...")

    # Generate executive summaries (Markdown, HTML, and Email formats)
    exec_summary_md = generate_executive_summary(analysis, output_dir)
    print(f"  ✅ Executive Summary (Markdown): {exec_summary_md}")

    exec_summary_html = generate_executive_summary_html(analysis, output_dir)
    print(f"  ✅ Executive Summary (HTML): {exec_summary_html}")

    exec_summary_email = generate_executive_summary_email(analysis, output_dir)
    print(f"  ✅ Executive Summary (Email): {exec_summary_email}")

    # Generate JSON report
    json_report = generate_json_report(analysis, output_dir)
    print(f"  ✅ JSON Report: {json_report}")

    # Generate text report
    text_report = generate_text_report(analysis, output_dir)
    print(f"  ✅ Text Report: {text_report}")

    # Generate enhanced failure report if requested
    if args.enhanced:
        failure_report = analyzer.generate_failure_report(test_results)
        failure_report_path = output_dir / f"failure_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(failure_report_path, 'w', encoding='utf-8') as f:
            json.dump(failure_report, f, indent=2)
        print(f"  ✅ Failure Analysis: {failure_report_path}")

        # Show recommendations
        recommendations = failure_report.get('recommendations', [])
        if recommendations:
            print("\n🎯 Priority Recommendations:")
            for rec in recommendations:
                print(f"  {rec['priority']} PRIORITY: {rec['area']} ({rec['count']} issues)")
                print(f"    → {rec['action']}")

    print("\n" + "=" * 60)
    print("✅ Analysis completed successfully!")
    print(f"📂 Reports saved to: {output_dir.absolute()}")
    print("=" * 60)

    # Email-friendly report guidance
    print("\n📧 Email-Ready Reports Generated:")
    print(f"  • HTML Report: Open {exec_summary_html.name} in browser and send as email")
    print(f"  • Plain Text: Copy content from {exec_summary_email.name} for email body")
    print(f"  • Attachment: Attach the HTML file to your email for stakeholders")
    print("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Analysis cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
