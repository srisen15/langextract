"""
Test Log Analyzer - Extract useful information from Playwright test execution logs
Enhanced for production use with failure categorization and batch processing
"""

import json
import re
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import csv
from pathlib import Path

class FailureCategory(Enum):
    """Categories of test failures for triage"""
    ASSERTION_FAILURE = "Assertion Failure"
    TIMEOUT = "Timeout"
    NETWORK_ERROR = "Network/API Error"
    ELEMENT_NOT_FOUND = "Element Not Found"
    AUTHENTICATION_ERROR = "Authentication Error"
    DATA_ISSUE = "Data/State Issue"
    BROWSER_ERROR = "Browser/Infrastructure Error"
    ENVIRONMENT_ISSUE = "Environment Issue"
    FLAKY_TEST = "Flaky Test"
    UNKNOWN = "Unknown"

class Priority(Enum):
    """Priority levels for test failures"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

@dataclass
class TestExecutionSummary:
    """Enhanced summary of test execution details"""
    test_name: str
    full_name: str
    status: str
    duration_ms: int
    duration_seconds: float
    failure_reason: str
    error_location: str
    retries_count: int
    test_file: str
    tags: List[str]
    failure_category: str
    priority: str
    is_flaky: bool
    environment: str
    needs_attention: bool
    
class TestLogExtractor:
    """Extract and analyze information from Playwright test execution logs"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.test_data = None
        self.load_test_data()
    
    def load_test_data(self):
        """Load JSON test data from file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.test_data = json.load(file)
        except Exception as e:
            print(f"Error loading test data: {e}")
            return None
    
    def categorize_failure(self) -> tuple[FailureCategory, Priority]:
        """Categorize the failure type and assign priority"""
        if not self.test_data or self.test_data.get('status') != 'failed':
            return FailureCategory.UNKNOWN, Priority.LOW
        
        failure_message = self.test_data.get('statusMessage', '').lower()
        status_trace = self.test_data.get('statusTrace', '').lower()
        test_name = self.test_data.get('name', '').lower()
        
        # Check for flaky test indicators
        is_flaky = self.test_data.get('retriesCount', 0) > 0 or self.test_data.get('flaky', False)
        
        # Categorization rules based on error patterns
        
        # Authentication/Authorization errors
        if any(keyword in failure_message for keyword in ['unauthorized', 'forbidden', 'authentication', 'login', 'credentials']):
            return FailureCategory.AUTHENTICATION_ERROR, Priority.HIGH
        
        # Timeout errors
        if any(keyword in failure_message for keyword in ['timeout', 'timed out', 'waiting for']) or 'timeout' in status_trace:
            return FailureCategory.TIMEOUT, Priority.MEDIUM if is_flaky else Priority.HIGH
        
        # Element not found errors
        if any(keyword in failure_message for keyword in ['element not found', 'selector', 'locator', 'not visible']):
            return FailureCategory.ELEMENT_NOT_FOUND, Priority.MEDIUM
        
        # Network/API errors
        if any(keyword in failure_message for keyword in ['network', 'connection', 'fetch', 'api', 'http', '500', '502', '503', '504']):
            return FailureCategory.NETWORK_ERROR, Priority.HIGH
        
        # Assertion failures
        if 'expect(' in failure_message or 'assertion' in failure_message or 'tocontain' in failure_message.replace(' ', ''):
            # Check if it's a data-related assertion
            if any(keyword in failure_message for keyword in ['submit failed', 'pending', 'status', 'state']):
                return FailureCategory.DATA_ISSUE, Priority.HIGH
            return FailureCategory.ASSERTION_FAILURE, Priority.MEDIUM
        
        # Browser/Infrastructure errors
        if any(keyword in failure_message for keyword in ['browser', 'page crash', 'navigation', 'protocol']):
            return FailureCategory.BROWSER_ERROR, Priority.MEDIUM
        
        # Environment issues
        if any(keyword in failure_message for keyword in ['environment', 'configuration', 'permission']):
            return FailureCategory.ENVIRONMENT_ISSUE, Priority.LOW
        
        # Flaky test detection
        if is_flaky:
            return FailureCategory.FLAKY_TEST, Priority.LOW
        
        return FailureCategory.UNKNOWN, Priority.MEDIUM
    
    def extract_environment_info(self) -> str:
        """Extract environment information from test data"""
        labels = self.test_data.get('labels', []) if self.test_data else []
        
        # Look for environment indicators
        for label in labels:
            if label.get('name') == 'host':
                return label.get('value', 'unknown')
            elif label.get('name') == 'environment':
                return label.get('value', 'unknown')
        
        # Check project/browser info
        parameters = self.test_data.get('parameters', []) if self.test_data else []
        for param in parameters:
            if param.get('name') == 'Project':
                return param.get('value', 'unknown')
        
        return 'unknown'
    
    def determine_needs_attention(self, category: FailureCategory, priority: Priority) -> bool:
        """Determine if this failure needs immediate attention"""
        high_priority_categories = [
            FailureCategory.AUTHENTICATION_ERROR,
            FailureCategory.NETWORK_ERROR,
            FailureCategory.DATA_ISSUE
        ]
        
        return (
            priority in [Priority.CRITICAL, Priority.HIGH] or
            category in high_priority_categories or
            (category == FailureCategory.TIMEOUT and priority != Priority.LOW)
        )
    
    def extract_basic_info(self) -> TestExecutionSummary:
        """Extract basic test execution information with categorization"""
        if not self.test_data:
            return None
            
        # Extract tags from labels
        tags = [label['value'] for label in self.test_data.get('labels', []) if label['name'] == 'tag']
        
        # Extract test file path
        test_file = self.test_data.get('fullName', '').split(':')[0] if ':' in self.test_data.get('fullName', '') else ''
        
        # Categorize failure
        failure_category, priority = self.categorize_failure()
        
        # Check if flaky
        is_flaky = self.test_data.get('retriesCount', 0) > 0 or self.test_data.get('flaky', False)
        
        # Determine if needs attention
        needs_attention = self.determine_needs_attention(failure_category, priority)
        
        return TestExecutionSummary(
            test_name=self.test_data.get('name', ''),
            full_name=self.test_data.get('fullName', ''),
            status=self.test_data.get('status', ''),
            duration_ms=self.test_data.get('time', {}).get('duration', 0),
            duration_seconds=self.test_data.get('time', {}).get('duration', 0) / 1000,
            failure_reason=self.test_data.get('statusMessage', ''),
            error_location=self.extract_error_location(),
            retries_count=self.test_data.get('retriesCount', 0),
            test_file=test_file,
            tags=tags,
            failure_category=failure_category.value,
            priority=priority.value,
            is_flaky=is_flaky,
            environment=self.extract_environment_info(),
            needs_attention=needs_attention
        )
    
    def extract_error_location(self) -> str:
        """Extract specific line number and file where error occurred"""
        status_trace = self.test_data.get('statusTrace', '')
        if status_trace:
            # Look for file path and line number pattern
            match = re.search(r'at (.+\.ts):(\d+):(\d+)', status_trace)
            if match:
                return f"{match.group(1)} (line {match.group(2)})"
        return ''
    
    def extract_test_steps(self) -> List[Dict[str, Any]]:
        """Extract all test steps with their status and timing"""
        steps = []
        test_stage = self.test_data.get('testStage', {})
        
        def extract_steps_recursive(step_list, parent_name=''):
            for step in step_list:
                step_info = {
                    'name': step.get('name', ''),
                    'full_name': f"{parent_name} > {step.get('name', '')}" if parent_name else step.get('name', ''),
                    'status': step.get('status', ''),
                    'duration_ms': step.get('time', {}).get('duration', 0),
                    'duration_seconds': step.get('time', {}).get('duration', 0) / 1000,
                    'has_error': bool(step.get('statusMessage', '')),
                    'error_message': step.get('statusMessage', '')
                }
                steps.append(step_info)
                
                # Recursively extract nested steps
                if step.get('steps'):
                    extract_steps_recursive(step.get('steps', []), step_info['full_name'])
        
        extract_steps_recursive(test_stage.get('steps', []))
        return steps
    
    def extract_api_calls(self) -> List[Dict[str, Any]]:
        """Extract API calls made during the test"""
        api_calls = []
        steps = self.extract_test_steps()
        
        for step in steps:
            step_name = step['name']
            if any(method in step_name for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']):
                # Extract HTTP method and endpoint
                match = re.match(r'(GET|POST|PUT|DELETE|PATCH)\s+"([^"]+)"', step_name)
                if match:
                    api_calls.append({
                        'method': match.group(1),
                        'endpoint': match.group(2),
                        'duration_ms': step['duration_ms'],
                        'status': step['status'],
                        'error': step.get('error_message', '')
                    })
        
        return api_calls
    
    def extract_ui_interactions(self) -> List[Dict[str, Any]]:
        """Extract UI interactions (clicks, fills, navigations)"""
        ui_interactions = []
        steps = self.extract_test_steps()
        
        ui_keywords = ['Click', 'Fill', 'Navigate', 'Wait for', 'Expect', 'Press']
        
        for step in steps:
            step_name = step['name']
            if any(keyword in step_name for keyword in ui_keywords):
                ui_interactions.append({
                    'action': step_name,
                    'duration_ms': step['duration_ms'],
                    'status': step['status'],
                    'error': step.get('error_message', '')
                })
        
        return ui_interactions
    
    def extract_timing_analysis(self) -> Dict[str, Any]:
        """Analyze timing patterns in the test execution"""
        steps = self.extract_test_steps()
        
        # Find slowest steps
        sorted_steps = sorted(steps, key=lambda x: x['duration_ms'], reverse=True)
        slowest_steps = sorted_steps[:5]
        
        # Calculate timing stats
        durations = [step['duration_ms'] for step in steps if step['duration_ms'] > 0]
        
        return {
            'total_duration_seconds': self.test_data.get('time', {}).get('duration', 0) / 1000,
            'slowest_steps': slowest_steps,
            'average_step_duration_ms': sum(durations) / len(durations) if durations else 0,
            'total_steps': len(steps),
            'failed_steps': len([s for s in steps if s['status'] == 'failed'])
        }
    
    def generate_test_report(self) -> str:
        """Generate a comprehensive test execution report"""
        if not self.test_data:
            return "Error: No test data loaded"
        
        summary = self.extract_basic_info()
        api_calls = self.extract_api_calls()
        ui_interactions = self.extract_ui_interactions()
        timing = self.extract_timing_analysis()
        
        report = f"""
# Test Execution Report

## Basic Information
- **Test Name**: {summary.test_name}
- **File**: {summary.test_file}
- **Status**: {summary.status}
- **Duration**: {summary.duration_seconds:.2f} seconds
- **Retries**: {summary.retries_count}
- **Tags**: {', '.join(summary.tags)}

## Failure Analysis
- **Failure Reason**: {summary.failure_reason}
- **Error Location**: {summary.error_location}

## Performance Analysis
- **Total Duration**: {timing['total_duration_seconds']:.2f} seconds
- **Total Steps**: {timing['total_steps']}
- **Failed Steps**: {timing['failed_steps']}
- **Average Step Duration**: {timing['average_step_duration_ms']:.0f}ms

## Slowest Operations
"""
        
        for i, step in enumerate(timing['slowest_steps'][:3], 1):
            report += f"{i}. **{step['name']}** - {step['duration_seconds']:.2f}s\n"
        
        report += f"""
## API Calls ({len(api_calls)} total)
"""
        for call in api_calls:
            status_icon = "✅" if call['status'] == 'passed' else "❌"
            report += f"- {status_icon} {call['method']} {call['endpoint']} ({call['duration_ms']}ms)\n"
        
        report += f"""
## Key UI Interactions
"""
        # Show only key interactions (not all)
        key_interactions = [ui for ui in ui_interactions if any(keyword in ui['action'] for keyword in ['Navigate', 'Click getByRole', 'Fill', 'Expect "toContain"'])][:10]
        
        for interaction in key_interactions:
            status_icon = "✅" if interaction['status'] == 'passed' else "❌"
            report += f"- {status_icon} {interaction['action']} ({interaction['duration_ms']}ms)\n"
        
        return report
    
    def extract_failure_context(self) -> Dict[str, Any]:
        """Extract context around the failure for debugging"""
        if self.test_data.get('status') != 'failed':
            return {'is_failed': False}
        
        # Find the failed step
        steps = self.extract_test_steps()
        failed_steps = [s for s in steps if s['status'] == 'failed']
        
        # Get steps around the failure
        all_steps = self.extract_test_steps()
        failure_context = []
        
        if failed_steps:
            failed_step = failed_steps[0]
            # Find index of failed step
            for i, step in enumerate(all_steps):
                if step['name'] == failed_step['name'] and step['status'] == 'failed':
                    # Get 3 steps before and 2 steps after
                    start_idx = max(0, i - 3)
                    end_idx = min(len(all_steps), i + 3)
                    failure_context = all_steps[start_idx:end_idx]
                    break
        
        return {
            'is_failed': True,
            'failure_reason': self.test_data.get('statusMessage', ''),
            'failure_location': self.extract_error_location(),
            'context_steps': failure_context,
            'expected_vs_actual': self.extract_assertion_details()
        }
    
    def extract_assertion_details(self) -> Dict[str, str]:
        """Extract expected vs actual values from assertion failures"""
        status_message = self.test_data.get('statusMessage', '')
        
        expected_match = re.search(r'Expected substring:\s*"([^"]+)"', status_message)
        received_match = re.search(r'Received string:\s*"([^"]+)"', status_message)
        
        return {
            'expected': expected_match.group(1) if expected_match else '',
            'actual': received_match.group(1) if received_match else ''
        }

class BatchTestAnalyzer:
    """Batch analyzer for multiple test log files"""
    
    def __init__(self, log_directory: str):
        self.log_directory = log_directory
        self.results: List[TestExecutionSummary] = []
        self.analysis_timestamp = datetime.now()
    
    def find_log_files(self, pattern: str = "*.json") -> List[str]:
        """Find all test log files in the directory"""
        log_files = []
        search_path = os.path.join(self.log_directory, pattern)
        log_files = glob.glob(search_path)
        
        # Also search in subdirectories
        recursive_path = os.path.join(self.log_directory, "**", pattern)
        log_files.extend(glob.glob(recursive_path, recursive=True))
        
        return list(set(log_files))  # Remove duplicates
    
    def analyze_all_logs(self, pattern: str = "*.json") -> List[TestExecutionSummary]:
        """Analyze all log files in the directory"""
        log_files = self.find_log_files(pattern)
        self.results = []
        
        print(f"Found {len(log_files)} log files to analyze...")
        
        for i, log_file in enumerate(log_files, 1):
            try:
                print(f"Processing {i}/{len(log_files)}: {os.path.basename(log_file)}")
                extractor = TestLogExtractor(log_file)
                summary = extractor.extract_basic_info()
                if summary:
                    self.results.append(summary)
            except Exception as e:
                print(f"Error processing {log_file}: {e}")
        
        return self.results
    
    def generate_failure_summary(self) -> Dict[str, Any]:
        """Generate summary statistics of failures"""
        if not self.results:
            return {}
        
        failed_tests = [r for r in self.results if r.status == 'failed']
        
        # Category breakdown
        category_counts = {}
        priority_counts = {}
        needs_attention_count = 0
        flaky_count = 0
        
        for test in failed_tests:
            category_counts[test.failure_category] = category_counts.get(test.failure_category, 0) + 1
            priority_counts[test.priority] = priority_counts.get(test.priority, 0) + 1
            if test.needs_attention:
                needs_attention_count += 1
            if test.is_flaky:
                flaky_count += 1
        
        return {
            'total_tests': len(self.results),
            'failed_tests': len(failed_tests),
            'passed_tests': len([r for r in self.results if r.status == 'passed']),
            'failure_rate': len(failed_tests) / len(self.results) * 100 if self.results else 0,
            'category_breakdown': category_counts,
            'priority_breakdown': priority_counts,
            'needs_attention': needs_attention_count,
            'flaky_tests': flaky_count,
            'environments': list(set([r.environment for r in self.results]))
        }
    
    def get_high_priority_failures(self) -> List[TestExecutionSummary]:
        """Get failures that need immediate attention"""
        return [r for r in self.results if r.needs_attention and r.status == 'failed']
    
    def get_flaky_tests(self) -> List[TestExecutionSummary]:
        """Get tests that appear to be flaky"""
        return [r for r in self.results if r.is_flaky]
    
    def export_to_csv(self, output_file: str = None) -> str:
        """Export results to CSV for further analysis"""
        if not output_file:
            timestamp = self.analysis_timestamp.strftime("%Y%m%d_%H%M%S")
            output_file = f"test_analysis_{timestamp}.csv"
        
        output_path = os.path.join(self.log_directory, output_file)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if not self.results:
                return output_path
            
            fieldnames = list(asdict(self.results[0]).keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(asdict(result))
        
        return output_path
    
    def generate_html_report(self, output_file: str = None) -> str:
        """Generate an HTML report for stakeholders"""
        if not output_file:
            timestamp = self.analysis_timestamp.strftime("%Y%m%d_%H%M%S")
            output_file = f"test_report_{timestamp}.html"
        
        output_path = os.path.join(self.log_directory, output_file)
        summary = self.generate_failure_summary()
        high_priority = self.get_high_priority_failures()
        flaky_tests = self.get_flaky_tests()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
        .critical {{ background-color: #ffebee; }}
        .warning {{ background-color: #fff3e0; }}
        .success {{ background-color: #e8f5e8; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .priority-critical {{ color: #d32f2f; font-weight: bold; }}
        .priority-high {{ color: #f57c00; font-weight: bold; }}
        .priority-medium {{ color: #1976d2; }}
        .priority-low {{ color: #388e3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Execution Analysis Report</h1>
        <p>Generated on: {self.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Total Tests Analyzed: {summary.get('total_tests', 0)}</p>
    </div>
    
    <div class="summary">
        <div class="metric success">
            <h3>{summary.get('passed_tests', 0)}</h3>
            <p>Passed Tests</p>
        </div>
        <div class="metric critical">
            <h3>{summary.get('failed_tests', 0)}</h3>
            <p>Failed Tests</p>
        </div>
        <div class="metric warning">
            <h3>{summary.get('needs_attention', 0)}</h3>
            <p>Need Attention</p>
        </div>
        <div class="metric warning">
            <h3>{summary.get('flaky_tests', 0)}</h3>
            <p>Flaky Tests</p>
        </div>
        <div class="metric">
            <h3>{summary.get('failure_rate', 0):.1f}%</h3>
            <p>Failure Rate</p>
        </div>
    </div>
    
    <h2>Failure Categories</h2>
    <table>
        <tr><th>Category</th><th>Count</th><th>Percentage</th></tr>
"""
        
        total_failures = summary.get('failed_tests', 1)
        for category, count in summary.get('category_breakdown', {}).items():
            percentage = (count / total_failures * 100) if total_failures > 0 else 0
            html_content += f"<tr><td>{category}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
        
        html_content += """
    </table>
    
    <h2>High Priority Failures (Need Immediate Attention)</h2>
    <table>
        <tr><th>Test Name</th><th>Category</th><th>Priority</th><th>Environment</th><th>Error</th></tr>
"""
        
        for test in high_priority[:10]:  # Show top 10
            priority_class = f"priority-{test.priority.lower()}"
            html_content += f"""
        <tr>
            <td>{test.test_name}</td>
            <td>{test.failure_category}</td>
            <td class="{priority_class}">{test.priority}</td>
            <td>{test.environment}</td>
            <td>{test.failure_reason[:100]}...</td>
        </tr>
"""
        
        html_content += """
    </table>
    
    <h2>Flaky Tests</h2>
    <table>
        <tr><th>Test Name</th><th>Retries</th><th>Category</th><th>Environment</th></tr>
"""
        
        for test in flaky_tests[:10]:  # Show top 10
            html_content += f"""
        <tr>
            <td>{test.test_name}</td>
            <td>{test.retries_count}</td>
            <td>{test.failure_category}</td>
            <td>{test.environment}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_actionable_report(self) -> str:
        """Generate actionable insights for the team"""
        summary = self.generate_failure_summary()
        high_priority = self.get_high_priority_failures()
        flaky_tests = self.get_flaky_tests()
        
        report = f"""
# Test Execution Analysis - Actionable Insights
Generated on: {self.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Executive Summary
- **Total Tests**: {summary.get('total_tests', 0)}
- **Failure Rate**: {summary.get('failure_rate', 0):.1f}%
- **Tests Needing Attention**: {summary.get('needs_attention', 0)}
- **Flaky Tests**: {summary.get('flaky_tests', 0)}

## 🚨 IMMEDIATE ACTION REQUIRED ({len(high_priority)} tests)
"""
        
        for test in high_priority:
            report += f"""
### {test.test_name}
- **Priority**: {test.priority}
- **Category**: {test.failure_category}
- **Environment**: {test.environment}
- **Error**: {test.failure_reason}
- **Location**: {test.error_location}
"""
        
        report += f"""
## 🔄 FLAKY TESTS TO INVESTIGATE ({len(flaky_tests)} tests)
"""
        
        for test in flaky_tests:
            report += f"""
### {test.test_name}
- **Retries**: {test.retries_count}
- **Category**: {test.failure_category}
- **Environment**: {test.environment}
"""
        
        # Recommendations based on failure patterns
        report += """
## 💡 RECOMMENDATIONS

"""
        
        category_counts = summary.get('category_breakdown', {})
        
        if category_counts.get('Data/State Issue', 0) > 0:
            report += "- **Data Issues**: Review test data setup and database state management\n"
        
        if category_counts.get('Timeout', 0) > 0:
            report += "- **Timeout Issues**: Investigate performance bottlenecks and increase timeout values\n"
        
        if category_counts.get('Network/API Error', 0) > 0:
            report += "- **API Issues**: Check API stability and error handling\n"
        
        if category_counts.get('Element Not Found', 0) > 0:
            report += "- **UI Issues**: Review page object selectors and wait strategies\n"
        
        if summary.get('flaky_tests', 0) > 3:
            report += "- **Flakiness**: Implement better wait strategies and retry mechanisms\n"
        
        return report

    def generate_csv_report(self, results: List[dict], output_file: str) -> str:
        """Generate CSV report from test results"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            if results:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for result in results:
                    writer.writerow(result)
        
        return output_file
    
    def generate_html_report(self, analysis: dict, results: List[dict], output_file: str) -> str:
        """Generate HTML report from analysis and results"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .failures {{ margin: 20px 0; }}
        .category {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .failed {{ color: #d32f2f; }}
        .passed {{ color: #388e3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Analysis Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>Total Tests</h3>
            <p>{analysis.get('total_tests', 0)}</p>
        </div>
        <div class="metric">
            <h3>Passed</h3>
            <p class="passed">{analysis.get('passed_tests', 0)}</p>
        </div>
        <div class="metric">
            <h3>Failed</h3>
            <p class="failed">{analysis.get('failed_tests', 0)}</p>
        </div>
        <div class="metric">
            <h3>Pass Rate</h3>
            <p>{100 - analysis.get('failure_rate', 0):.1f}%</p>
        </div>
    </div>
    
    <div class="failures">
        <h2>Failure Categories</h2>
"""
        
        # Add failure categories
        if analysis.get('category_breakdown'):
            for category, count in analysis['category_breakdown'].items():
                html_content += f'<div class="category"><strong>{category}:</strong> {count} failures</div>'
        
        html_content += """
    </div>
    
    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Status</th>
            <th>Duration (s)</th>
            <th>Category</th>
            <th>Environment</th>
        </tr>
"""
        
        # Add test results
        for result in results[:50]:  # Limit to first 50 for readability
            status_class = "passed" if result.get('status') == 'passed' else "failed"
            html_content += f"""
        <tr>
            <td>{result.get('test_name', 'N/A')}</td>
            <td class="{status_class}">{result.get('status', 'N/A')}</td>
            <td>{result.get('duration_seconds', 0):.2f}</td>
            <td>{result.get('failure_category', 'N/A')}</td>
            <td>{result.get('environment', 'N/A')}</td>
        </tr>"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file

def main():
    """Main function to demonstrate usage"""
    # For single file analysis
    json_file = r"c:\Users\senthil.vivekanandan\Downloads\112048174313a20f.json"
    
    print("=== SINGLE FILE ANALYSIS ===")
    extractor = TestLogExtractor(json_file)
    summary = extractor.extract_basic_info()
    
    if summary:
        print(f"Test: {summary.test_name}")
        print(f"Status: {summary.status}")
        print(f"Category: {summary.failure_category}")
        print(f"Priority: {summary.priority}")
        print(f"Needs Attention: {summary.needs_attention}")
        print(f"Is Flaky: {summary.is_flaky}")
    
    print(extractor.generate_test_report())
    
    print("\n=== FAILURE ANALYSIS ===")
    failure_context = extractor.extract_failure_context()
    if failure_context['is_failed']:
        print(f"Expected: '{failure_context['expected_vs_actual']['expected']}'")
        print(f"Actual: '{failure_context['expected_vs_actual']['actual']}'")
        print(f"Location: {failure_context['failure_location']}")

def batch_analysis_example():
    """Example of batch analysis for production use"""
    # Example: analyze all JSON files in a directory
    log_directory = r"c:\Users\senthil.vivekanandan\Downloads"  # Change this to your log directory
    
    analyzer = BatchTestAnalyzer(log_directory)
    results = analyzer.analyze_all_logs()
    
    # Generate summary
    summary = analyzer.generate_failure_summary()
    print(f"""
=== BATCH ANALYSIS RESULTS ===
Total Tests: {summary['total_tests']}
Failed Tests: {summary['failed_tests']}
Failure Rate: {summary['failure_rate']:.1f}%
Tests Needing Attention: {summary['needs_attention']}
Flaky Tests: {summary['flaky_tests']}
""")
    
    # Show high priority failures
    high_priority = analyzer.get_high_priority_failures()
    if high_priority:
        print(f"\n🚨 HIGH PRIORITY FAILURES ({len(high_priority)} tests):")
        for test in high_priority[:5]:  # Show top 5
            print(f"- {test.test_name} [{test.failure_category}] - {test.priority}")
    
    # Export results
    csv_file = analyzer.export_to_csv()
    html_file = analyzer.generate_html_report()
    
    print(f"\n📊 Reports generated:")
    print(f"- CSV: {csv_file}")
    print(f"- HTML: {html_file}")
    
    # Generate actionable insights
    insights = analyzer.generate_actionable_report()
    insights_file = os.path.join(log_directory, "actionable_insights.md")
    with open(insights_file, 'w', encoding='utf-8') as f:
        f.write(insights)
    print(f"- Insights: {insights_file}")

if __name__ == "__main__":
    main()
    print("\n" + "="*60)
    batch_analysis_example()