import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import csv

@dataclass
class TestCase:
    """Represents a single test case with metadata"""
    file_path: str
    test_name: str
    tags: List[str]
    line_number: int
    test_type: str  # 'test' or 'test.describe'
    estimated_duration: int = 60  # Default 60 seconds

@dataclass
class TagReport:
    """Report structure for tag analysis"""
    tag_name: str
    test_count: int
    files: Set[str]
    test_cases: List[TestCase]
    estimated_total_duration: int
    coverage_percentage: float

class PlaywrightTestTagAnalyzer:
    """
    Analyzes Playwright test files following MCP server architecture patterns
    Compatible with your existing test structure and Azure Pipeline integration
    """
    
    def __init__(self, test_directory: str = "tests", output_dir: str = "reports"):
        self.test_directory = Path(test_directory)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test file patterns following your project structure
        self.test_patterns = [
            "**/*.spec.ts",
            "**/*.test.ts", 
            "**/tests-dao/**/*.ts",
            "**/tests-legacy/**/*.ts"
        ]
        
        # Tag patterns based on your Azure Pipeline structure
        self.tag_regex = re.compile(r"tag:\s*\[([^\]]+)\]")
        self.test_regex = re.compile(r"test\s*\(\s*['\"`]([^'\"]+)['\"`]\s*,?\s*(?:\{[^}]*tag:\s*\[([^\]]+)\][^}]*\})?\s*,")
        self.describe_regex = re.compile(r"test\.describe\s*\(\s*['\"`]([^'\"]+)['\"`]")
        
        # MCP server compatible metadata
        self.mcp_metadata = {
            "framework": "playwright",
            "analyzer_version": "1.0.0",
            "architecture": "mcp-server-compatible",
            "azure_pipeline_tags": ["@smoke", "@regression", "@integrations", "@legacy", "@dao", "@proposal", "@e2e"]
        }

    def find_test_files(self) -> List[Path]:
        """Find all test files matching patterns"""
        test_files = []
        
        for pattern in self.test_patterns:
            test_files.extend(self.test_directory.glob(pattern))
        
        # Filter out non-test files
        test_files = [f for f in test_files if self._is_test_file(f)]
        
        print(f"🔍 Found {len(test_files)} test files")
        return test_files

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a valid test file"""
        if not file_path.suffix in ['.ts', '.js']:
            return False
            
        # Exclude config and utility files
        exclude_patterns = ['config', 'setup', 'fixture', 'util', 'helper']
        filename_lower = file_path.name.lower()
        
        return not any(pattern in filename_lower for pattern in exclude_patterns)

    def extract_tests_from_file(self, file_path: Path) -> List[TestCase]:
        """Extract test cases and their tags from a file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            test_cases = []
            
            # Track current describe block context
            current_describe_tags = []
            
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Check for test.describe blocks
                describe_match = self.describe_regex.search(line_stripped)
                if describe_match:
                    describe_name = describe_match.group(1)
                    # Look for tags in the same line or nearby lines
                    describe_tags = self._extract_tags_from_line(line_stripped)
                    current_describe_tags = describe_tags
                    continue
                
                # Check for individual test cases
                test_match = self.test_regex.search(line_stripped)
                if test_match:
                    test_name = test_match.group(1)
                    
                    # Extract tags from the test line
                    test_tags = self._extract_tags_from_line(line_stripped)
                    
                    # If no tags in test line, look in nearby lines
                    if not test_tags:
                        test_tags = self._find_tags_near_line(lines, line_num - 1)
                    
                    # Combine with describe block tags
                    all_tags = list(set(current_describe_tags + test_tags))
                    
                    # Estimate duration based on tags (following your Azure Pipeline patterns)
                    estimated_duration = self._estimate_test_duration(all_tags)
                    
                    test_case = TestCase(
                        file_path=str(file_path.relative_to(self.test_directory)),
                        test_name=test_name,
                        tags=all_tags,
                        line_number=line_num,
                        test_type='test',
                        estimated_duration=estimated_duration
                    )
                    
                    test_cases.append(test_case)
            
            return test_cases
            
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return []

    def _extract_tags_from_line(self, line: str) -> List[str]:
        """Extract tags from a single line"""
        tags = []
        
        # Pattern 1: tag: ['@smoke', '@regression']
        tag_match = self.tag_regex.search(line)
        if tag_match:
            tag_content = tag_match.group(1)
            # Extract individual tags
            tag_values = re.findall(r"['\"`]([^'\"]+)['\"`]", tag_content)
            tags.extend(tag_values)
        
        # Pattern 2: Look for @tags in comments or strings
        at_tags = re.findall(r"@[\w-]+", line)
        tags.extend(at_tags)
        
        return [tag.strip() for tag in tags if tag.strip()]

    def _find_tags_near_line(self, lines: List[str], target_line: int, search_range: int = 3) -> List[str]:
        """Find tags in lines near the target line"""
        tags = []
        start = max(0, target_line - search_range)
        end = min(len(lines), target_line + search_range)
        
        for i in range(start, end):
            line_tags = self._extract_tags_from_line(lines[i])
            tags.extend(line_tags)
        
        return tags

    def _estimate_test_duration(self, tags: List[str]) -> int:
        """Estimate test duration based on tags (following Azure Pipeline patterns)"""
        duration_map = {
            '@smoke': 30,      # Quick smoke tests
            '@regression': 90,  # Longer regression tests
            '@integrations': 120, # Integration tests
            '@e2e': 180,       # End-to-end tests
            '@dao': 60,        # DAO-specific tests
            '@proposal': 45,   # Proposal workflow tests
            '@legacy': 75      # Legacy system tests
        }
        
        # Use the maximum duration for any matching tag
        max_duration = 60  # Default
        for tag in tags:
            if tag in duration_map:
                max_duration = max(max_duration, duration_map[tag])
        
        return max_duration

    def analyze_tags(self, test_cases: List[TestCase]) -> Dict[str, TagReport]:
        """Analyze test cases and generate tag reports"""
        tag_data = defaultdict(lambda: {
            'test_count': 0,
            'files': set(),
            'test_cases': [],
            'total_duration': 0
        })
        
        total_tests = len(test_cases)
        
        # Process each test case
        for test_case in test_cases:
            for tag in test_case.tags:
                tag_data[tag]['test_count'] += 1
                tag_data[tag]['files'].add(test_case.file_path)
                tag_data[tag]['test_cases'].append(test_case)
                tag_data[tag]['total_duration'] += test_case.estimated_duration
        
        # Convert to TagReport objects
        tag_reports = {}
        for tag, data in tag_data.items():
            coverage_percentage = (data['test_count'] / total_tests * 100) if total_tests > 0 else 0
            
            tag_reports[tag] = TagReport(
                tag_name=tag,
                test_count=data['test_count'],
                files=data['files'],
                test_cases=data['test_cases'],
                estimated_total_duration=data['total_duration'],
                coverage_percentage=coverage_percentage
            )
        
        return tag_reports

    def generate_reports(self) -> Dict[str, any]:
        """Generate comprehensive test tag reports"""
        print("🚀 Starting test tag analysis for MCP server...")
        
        # Find and analyze test files
        test_files = self.find_test_files()
        all_test_cases = []
        
        for test_file in test_files:
            test_cases = self.extract_tests_from_file(test_file)
            all_test_cases.extend(test_cases)
            print(f"📄 {test_file.name}: {len(test_cases)} tests")
        
        print(f"✅ Total tests found: {len(all_test_cases)}")
        
        # Analyze tags
        tag_reports = self.analyze_tags(all_test_cases)
        
        # Generate summary statistics
        summary = self._generate_summary(all_test_cases, tag_reports)
        
        # Generate output files
        self._write_json_report(tag_reports, summary)
        self._write_csv_report(tag_reports)
        self._write_console_report(tag_reports, summary)
        self._write_mcp_compatible_report(tag_reports, summary)
        
        return {
            'summary': summary,
            'tag_reports': tag_reports,
            'total_tests': len(all_test_cases),
            'mcp_metadata': self.mcp_metadata
        }

    def _generate_summary(self, test_cases: List[TestCase], tag_reports: Dict[str, TagReport]) -> Dict:
        """Generate summary statistics"""
        file_distribution = defaultdict(int)
        for test_case in test_cases:
            file_distribution[test_case.file_path] += 1
        
        # Azure Pipeline tag analysis (based on your pipeline structure)
        azure_tags = ['@smoke', '@regression', '@integrations', '@legacy']
        azure_coverage = {}
        for tag in azure_tags:
            azure_coverage[tag] = tag_reports.get(tag, TagReport(tag, 0, set(), [], 0, 0)).test_count
        
        return {
            'total_tests': len(test_cases),
            'total_tags': len(tag_reports),
            'total_files': len(file_distribution),
            'azure_pipeline_coverage': azure_coverage,
            'estimated_total_duration_minutes': sum(tc.estimated_duration for tc in test_cases) // 60,
            'top_tags': sorted(tag_reports.items(), key=lambda x: x[1].test_count, reverse=True)[:10],
            'file_distribution': dict(file_distribution),
            'mcp_server_compatible': True
        }

    def _write_json_report(self, tag_reports: Dict[str, TagReport], summary: Dict):
        """Write detailed JSON report"""
        report_data = {
            'metadata': self.mcp_metadata,
            'summary': summary,
            'tag_reports': {}
        }
        
        # Convert TagReport objects to dictionaries
        for tag, report in tag_reports.items():
            report_dict = asdict(report)
            # Convert sets to lists for JSON serialization
            report_dict['files'] = list(report_dict['files'])
            # Convert test_cases to simplified format
            report_dict['test_cases'] = [
                {
                    'file_path': tc.file_path,
                    'test_name': tc.test_name,
                    'line_number': tc.line_number,
                    'estimated_duration': tc.estimated_duration
                }
                for tc in report.test_cases
            ]
            report_data['tag_reports'][tag] = report_dict
        
        output_file = self.output_dir / 'test_tag_report.json'
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 JSON report written to: {output_file}")

    def _write_csv_report(self, tag_reports: Dict[str, TagReport]):
        """Write CSV summary report"""
        output_file = self.output_dir / 'test_tag_summary.csv'
        
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['tag_name', 'test_count', 'file_count', 'coverage_percentage', 'estimated_duration_minutes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for tag, report in sorted(tag_reports.items(), key=lambda x: x[1].test_count, reverse=True):
                writer.writerow({
                    'tag_name': report.tag_name,
                    'test_count': report.test_count,
                    'file_count': len(report.files),
                    'coverage_percentage': f"{report.coverage_percentage:.1f}%",
                    'estimated_duration_minutes': report.estimated_total_duration // 60
                })
        
        print(f"📈 CSV report written to: {output_file}")

    def _write_console_report(self, tag_reports: Dict[str, TagReport], summary: Dict):
        """Write human-readable console report"""
        print("\n" + "="*60)
        print("🎯 PLAYWRIGHT TEST TAG ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Total Tags: {summary['total_tags']}")
        print(f"   Total Files: {summary['total_files']}")
        print(f"   Estimated Duration: {summary['estimated_total_duration_minutes']} minutes")
        
        print(f"\n🚀 AZURE PIPELINE TAG COVERAGE:")
        for tag, count in summary['azure_pipeline_coverage'].items():
            print(f"   {tag}: {count} tests")
        
        print(f"\n🏷️  TOP TAGS BY TEST COUNT:")
        for tag, report in summary['top_tags']:
            print(f"   {tag}: {report.test_count} tests ({report.coverage_percentage:.1f}% coverage)")
        
        print(f"\n📁 FILE DISTRIBUTION:")
        for file_path, count in list(summary['file_distribution'].items())[:10]:
            print(f"   {file_path}: {count} tests")
        
        print("\n" + "="*60)

    def _write_mcp_compatible_report(self, tag_reports: Dict[str, TagReport], summary: Dict):
        """Write MCP server compatible report for tool registry integration"""
        mcp_tools = []
        
        # Generate tool definitions for each significant tag
        for tag, report in tag_reports.items():
            if report.test_count >= 3:  # Only include tags with multiple tests
                tool_definition = {
                    "id": f"playwright-{tag.replace('@', '').replace('-', '_')}-suite",
                    "name": f"playwright-{tag.replace('@', '')}-suite",
                    "type": "playwright",
                    "command": f"npx playwright test --grep='{tag}' --config=playwright.config.ts",
                    "tags": [tag],
                    "supportedPersonas": self._get_personas_for_tag(tag),
                    "estimatedDuration": report.estimated_total_duration,
                    "requiresAuthentication": self._requires_auth(tag),
                    "owner": "qa-team",
                    "metadata": {
                        "testCount": report.test_count,
                        "fileCount": len(report.files),
                        "azurePipelineCompatible": tag in ['@smoke', '@regression', '@integrations'],
                        "coverage": f"{report.coverage_percentage:.1f}%"
                    }
                }
                mcp_tools.append(tool_definition)
        
        mcp_report = {
            "mcp_server_version": "1.0.0-mvp",
            "generated_at": summary.get('timestamp', 'unknown'),
            "total_tools": len(mcp_tools),
            "azure_pipeline_integration": True,
            "tools": mcp_tools,
            "summary": summary
        }
        
        output_file = self.output_dir / 'mcp_tools_registry.json'
        with open(output_file, 'w') as f:
            json.dump(mcp_report, f, indent=2)
        
        print(f"🔧 MCP tools registry written to: {output_file}")

    def _get_personas_for_tag(self, tag: str) -> List[str]:
        """Determine supported personas for a tag"""
        # Default to all personas unless tag suggests otherwise
        if 'dao' in tag.lower():
            return ['HNW', 'KPWS']  # DAO typically for higher-value clients
        elif 'legacy' in tag.lower():
            return ['KAS']  # Legacy might be more for KAS
        else:
            return ['HNW', 'KAS', 'KPWS']

    def _requires_auth(self, tag: str) -> bool:
        """Determine if tag requires authentication"""
        auth_required_tags = ['@dao', '@proposal', '@e2e', '@regression', '@integrations']
        return any(auth_tag in tag.lower() for auth_tag in auth_required_tags)


def main():
    """Main execution function with CLI interface"""
    parser = argparse.ArgumentParser(
        description="Generate test tag reports for Playwright tests (MCP Server compatible)"
    )
    parser.add_argument(
        '--test-dir', 
        default='tests', 
        help='Directory containing test files (default: tests)'
    )
    parser.add_argument(
        '--output-dir', 
        default='reports', 
        help='Output directory for reports (default: reports)'
    )
    parser.add_argument(
        '--format', 
        choices=['all', 'json', 'csv', 'console', 'mcp'], 
        default='all',
        help='Output format (default: all)'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = PlaywrightTestTagAnalyzer(
        test_directory=args.test_dir,
        output_dir=args.output_dir
    )
    
    # Generate reports
    try:
        results = analyzer.generate_reports()
        print(f"\n✅ Analysis complete! Reports generated in {args.output_dir}/")
        print(f"🎯 Found {results['total_tests']} tests across {results['summary']['total_tags']} tags")
        return 0
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())