#!/usr/bin/env python3
"""
Enhanced CI/CD Integration Script for Test Log Analysis
Supports Azure Blob Storage, quality gates, and multiple CI platforms
"""

import argparse
import sys
import os
import json
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.test_log_analyzer import BatchTestAnalyzer, TestLogExtractor

class QualityGates:
    """Define and check quality gates for test results"""
    
    def __init__(self, config_file: str = None):
        """Initialize quality gates with optional config file"""
        self.gates = self.load_default_gates()
        if config_file and os.path.exists(config_file):
            self.load_gates_from_file(config_file)
    
    def load_default_gates(self):
        """Load default quality gate thresholds"""
        return {
            "max_failure_rate": 10.0,  # 10%
            "max_critical_failures": 0,
            "max_high_priority_failures": 5,
            "max_flaky_test_rate": 15.0,  # 15%
            "min_pass_rate": 85.0,  # 85%
            "max_timeout_failures": 3,
            "max_data_issue_failures": 2,
            "max_auth_failures": 0
        }
    
    def load_gates_from_file(self, config_file: str):
        """Load quality gates from JSON config file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.gates.update(config.get('quality_gates', {}))
        except Exception as e:
            print(f"Warning: Could not load quality gates config: {e}")
    
    def check_gates(self, results: dict) -> tuple[bool, list]:
        """
        Check if results pass quality gates
        
        Returns:
            tuple: (passed, list of failed gate messages)
        """
        failures = []
        
        # Failure rate check
        if results['failure_rate'] > self.gates['max_failure_rate']:
            failures.append(f"Failure rate ({results['failure_rate']:.1f}%) exceeds threshold ({self.gates['max_failure_rate']}%)")
        
        # Critical failures check
        if results['critical_failures'] > self.gates['max_critical_failures']:
            failures.append(f"Critical failures ({results['critical_failures']}) exceed threshold ({self.gates['max_critical_failures']})")
        
        # High priority failures check
        if results['high_priority_failures'] > self.gates['max_high_priority_failures']:
            failures.append(f"High priority failures ({results['high_priority_failures']}) exceed threshold ({self.gates['max_high_priority_failures']})")
        
        # Flaky test rate check
        flaky_rate = (results['flaky_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
        if flaky_rate > self.gates['max_flaky_test_rate']:
            failures.append(f"Flaky test rate ({flaky_rate:.1f}%) exceeds threshold ({self.gates['max_flaky_test_rate']}%)")
        
        # Pass rate check
        pass_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
        if pass_rate < self.gates['min_pass_rate']:
            failures.append(f"Pass rate ({pass_rate:.1f}%) below minimum ({self.gates['min_pass_rate']}%)")
        
        # Category-specific checks
        categories = results.get('category_breakdown', {})
        
        if categories.get('Timeout', 0) > self.gates['max_timeout_failures']:
            failures.append(f"Timeout failures ({categories['Timeout']}) exceed threshold ({self.gates['max_timeout_failures']})")
        
        if categories.get('Data/State Issue', 0) > self.gates['max_data_issue_failures']:
            failures.append(f"Data issue failures ({categories['Data/State Issue']}) exceed threshold ({self.gates['max_data_issue_failures']})")
        
        if categories.get('Authentication Error', 0) > self.gates['max_auth_failures']:
            failures.append(f"Authentication failures ({categories['Authentication Error']}) exceed threshold ({self.gates['max_auth_failures']})")
        
        return len(failures) == 0, failures

class CIPlatformIntegration:
    """Integration with various CI/CD platforms"""
    
    @staticmethod
    def detect_platform():
        """Auto-detect CI platform from environment variables"""
        if os.environ.get('GITHUB_ACTIONS'):
            return 'github'
        elif os.environ.get('AZURE_DEVOPS') or os.environ.get('TF_BUILD'):
            return 'azure_devops'
        elif os.environ.get('JENKINS_URL'):
            return 'jenkins'
        elif os.environ.get('GITLAB_CI'):
            return 'gitlab'
        elif os.environ.get('CIRCLE_CI'):
            return 'circleci'
        else:
            return 'generic'
    
    @staticmethod
    def create_annotations(results: dict, platform: str = None):
        """Create platform-specific annotations"""
        if not platform:
            platform = CIPlatformIntegration.detect_platform()
        
        if platform == 'github':
            CIPlatformIntegration._github_annotations(results)
        elif platform == 'azure_devops':
            CIPlatformIntegration._azure_devops_annotations(results)
        elif platform == 'jenkins':
            CIPlatformIntegration._jenkins_annotations(results)
        elif platform == 'gitlab':
            CIPlatformIntegration._gitlab_annotations(results)
    
    @staticmethod
    def _github_annotations(results: dict):
        """Create GitHub Actions annotations"""
        if results['critical_failures'] > 0:
            print(f"::error::Found {results['critical_failures']} critical test failures")
        
        if results['high_priority_failures'] > 0:
            print(f"::warning::Found {results['high_priority_failures']} high priority test failures")
        
        if results['flaky_tests'] > 0:
            print(f"::notice::Found {results['flaky_tests']} flaky tests that should be investigated")
        
        # Set output variables
        print(f"::set-output name=failure_rate::{results['failure_rate']}")
        print(f"::set-output name=total_tests::{results['total_tests']}")
        print(f"::set-output name=failed_tests::{results['failed_tests']}")
    
    @staticmethod
    def _azure_devops_annotations(results: dict):
        """Create Azure DevOps annotations"""
        if results['critical_failures'] > 0:
            print(f"##vso[task.logissue type=error]Found {results['critical_failures']} critical test failures")
        
        if results['high_priority_failures'] > 0:
            print(f"##vso[task.logissue type=warning]Found {results['high_priority_failures']} high priority test failures")
        
        # Set variables
        print(f"##vso[task.setvariable variable=test.failure.rate]{results['failure_rate']}")
        print(f"##vso[task.setvariable variable=test.total.count]{results['total_tests']}")
    
    @staticmethod
    def _jenkins_annotations(results: dict):
        """Create Jenkins annotations"""
        # Jenkins doesn't have built-in annotations, but we can use build description
        if results['critical_failures'] > 0 or results['high_priority_failures'] > 0:
            print(f"JENKINS_BUILD_DESCRIPTION=Critical: {results['critical_failures']}, High Priority: {results['high_priority_failures']} failures")
    
    @staticmethod
    def _gitlab_annotations(results: dict):
        """Create GitLab CI annotations"""
        if results['critical_failures'] > 0:
            print(f"CRITICAL: Found {results['critical_failures']} critical test failures")
        
        if results['high_priority_failures'] > 0:
            print(f"WARNING: Found {results['high_priority_failures']} high priority test failures")

def main():
    """Enhanced main CI/CD integration function"""
    parser = argparse.ArgumentParser(
        description="Enhanced CI/CD Test Log Analysis with Quality Gates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local directory analysis
  python enhanced_ci_integration.py --directory ./test-results
  
  # Azure Blob Storage analysis
  python enhanced_ci_integration.py --azure-connection "DefaultEndpointsProtocol=https;..." --azure-container "test-logs"
  
  # With custom quality gates
  python enhanced_ci_integration.py --directory ./test-results --quality-gates-config quality_gates.json
        """
    )
    
    # Input source options
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--directory', help='Local directory containing test log files')
    source_group.add_argument('--file', help='Single test log file to analyze')
    source_group.add_argument('--azure-connection', help='Azure Storage connection string for blob analysis')
    
    # Azure-specific options
    parser.add_argument('--azure-container', help='Azure blob container name')
    parser.add_argument('--azure-prefix', default='', help='Azure blob prefix filter')
    parser.add_argument('--azure-days-back', type=int, default=1, help='Days back to analyze in Azure')
    
    # Quality gates options
    parser.add_argument('--quality-gates-config', help='JSON file with custom quality gate thresholds')
    parser.add_argument('--skip-quality-gates', action='store_true', help='Skip quality gate checks')
    
    # CI platform options
    parser.add_argument('--ci-platform', choices=['github', 'azure_devops', 'jenkins', 'gitlab', 'circleci', 'generic'], 
                       help='CI platform for annotations (auto-detected if not specified)')
    
    # Output options
    parser.add_argument('--output-dir', help='Output directory for reports')
    parser.add_argument('--export-metrics', help='Export metrics to JSON file')
    parser.add_argument('--quiet', action='store_true', help='Suppress console output')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        # Initialize quality gates
        quality_gates = QualityGates(args.quality_gates_config) if not args.skip_quality_gates else None
        
        # Determine analysis method and run
        if args.azure_connection:
            results = run_azure_analysis(args)
        elif args.file:
            results = analyze_single_file(args)
        else:
            results = analyze_directory(args)
        
        if not results:
            print("No test data found")
            return 1
        
        # Print summary
        if not args.quiet:
            print_enhanced_summary(results, args.verbose)
        
        # Check quality gates
        gate_passed = True
        if quality_gates:
            gate_passed, gate_failures = quality_gates.check_gates(results)
            
            if not gate_passed:
                print(f"\nQUALITY GATES FAILED:")
                for failure in gate_failures:
                    print(f"  - {failure}")
            else:
                print(f"\nALL QUALITY GATES PASSED")
        
        # Create CI platform annotations
        platform = args.ci_platform or CIPlatformIntegration.detect_platform()
        CIPlatformIntegration.create_annotations(results, platform)
        
        # Export metrics if requested
        if args.export_metrics:
            export_metrics_to_file(results, args.export_metrics)
        
        # Return appropriate exit code
        if not args.skip_quality_gates and not gate_passed:
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def run_azure_analysis(args) -> dict:
    """Run analysis using Azure Blob Storage"""
    if not args.azure_container:
        raise ValueError("Azure container name required for blob analysis")
    
    # Import and use Azure analyzer
    from azure_blob_analyzer import AzureBlobTestAnalyzer
    
    analyzer = AzureBlobTestAnalyzer(
        connection_string=args.azure_connection,
        container_name=args.azure_container,
        local_cache_dir=args.output_dir or "./azure_cache"
    )
    
    analysis_results = analyzer.run_daily_analysis(
        blob_prefix=args.azure_prefix,
        days_back=args.azure_days_back,
        upload_results=True,
        cleanup_local=True
    )
    
    if analysis_results["status"] != "success":
        raise RuntimeError(f"Azure analysis failed: {analysis_results.get('message', 'Unknown error')}")
    
    return analysis_results["stats"]

def analyze_directory(args) -> dict:
    """Analyze directory of test files"""
    if not os.path.exists(args.directory):
        raise FileNotFoundError(f"Directory not found: {args.directory}")
    
    analyzer = BatchTestAnalyzer(args.directory)
    analyzer.analyze_all_logs()
    
    return analyzer.generate_failure_summary()

def analyze_single_file(args) -> dict:
    """Analyze single test file"""
    if not os.path.exists(args.file):
        raise FileNotFoundError(f"File not found: {args.file}")
    
    extractor = TestLogExtractor(args.file)
    summary = extractor.extract_basic_info()
    
    if not summary:
        return None
    
    # Convert single test summary to batch format
    return {
        'total_tests': 1,
        'failed_tests': 1 if summary.status == 'failed' else 0,
        'passed_tests': 1 if summary.status == 'passed' else 0,
        'failure_rate': 100.0 if summary.status == 'failed' else 0.0,
        'critical_failures': 1 if summary.priority == 'Critical' else 0,
        'high_priority_failures': 1 if summary.priority == 'High' else 0,
        'needs_attention': 1 if summary.needs_attention else 0,
        'flaky_tests': 1 if summary.is_flaky else 0,
        'category_breakdown': {summary.failure_category: 1} if summary.status == 'failed' else {}
    }

def print_enhanced_summary(results: dict, verbose: bool = False):
    """Print enhanced CI-friendly summary"""
    print(f"""
TEST ANALYSIS RESULTS
========================
Total Tests: {results['total_tests']}
Passed: {results['passed_tests']} ({(results['passed_tests']/results['total_tests']*100):.1f}%)
Failed: {results['failed_tests']} ({results['failure_rate']:.1f}%)

PRIORITY BREAKDOWN:
   Critical: {results.get('critical_failures', 0)}
   High Priority: {results.get('high_priority_failures', 0)}
   Need Attention: {results.get('needs_attention', 0)}
   Flaky Tests: {results.get('flaky_tests', 0)}
""")
    
    if verbose and results.get('category_breakdown'):
        print("FAILURE CATEGORIES:")
        for category, count in sorted(results['category_breakdown'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / results['failed_tests'] * 100) if results['failed_tests'] > 0 else 0
            print(f"   {category}: {count} ({percentage:.1f}%)")

def export_metrics_to_file(results: dict, file_path: str):
    """Export metrics to JSON file for external systems"""
    metrics = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "test_metrics": results,
        "quality_score": calculate_quality_score(results),
        "recommendations": generate_recommendations(results)
    }
    
    with open(file_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics exported to: {file_path}")

def calculate_quality_score(results: dict) -> float:
    """Calculate overall quality score (0-100)"""
    pass_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 100
    
    # Deduct points for various issues
    deductions = 0
    deductions += results.get('critical_failures', 0) * 20  # 20 points per critical
    deductions += results.get('high_priority_failures', 0) * 10  # 10 points per high priority
    deductions += results.get('flaky_tests', 0) * 2  # 2 points per flaky test
    
    quality_score = max(0, pass_rate - deductions)
    return round(quality_score, 1)

def generate_recommendations(results: dict) -> list:
    """Generate actionable recommendations based on results"""
    recommendations = []
    
    if results.get('critical_failures', 0) > 0:
        recommendations.append("URGENT: Address critical failures immediately")
    
    if results['failure_rate'] > 15:
        recommendations.append("High failure rate detected - investigate test environment stability")
    
    if results.get('flaky_tests', 0) > 5:
        recommendations.append("Multiple flaky tests detected - review wait strategies and test data")
    
    categories = results.get('category_breakdown', {})
    if categories.get('Timeout', 0) > 2:
        recommendations.append("Multiple timeout failures - investigate performance issues")
    
    if categories.get('Authentication Error', 0) > 0:
        recommendations.append("Authentication failures detected - check credentials and auth service")
    
    return recommendations

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)