#!/usr/bin/env python3
"""
Test the Enhanced Test Analyzer
Validates enhanced categorization, environment mapping, and performance analytics
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Add core directory for direct imports
core_dir = os.path.join(src_dir, 'core')
sys.path.insert(0, core_dir)

def create_sample_test_data():
    """Create sample test data to validate enhanced analyzer"""
    
    sample_tests = [
        {
            'test_name': 'login_authentication_test',
            'status': 'failed',
            'duration_ms': 5500,
            'duration_seconds': 5.5,
            'failure_reason': 'Authentication failed: Invalid credentials provided',
            'environment': 'dev-linuxaa8d0014O1',
            'failure_category': 'unknown'
        },
        {
            'test_name': 'page_load_timeout_test',
            'status': 'failed', 
            'duration_ms': 32000,
            'duration_seconds': 32.0,
            'failure_reason': 'Timeout exceeded waiting for page to load',
            'environment': 'qa-server-east',
            'failure_category': 'unknown'
        },
        {
            'test_name': 'api_network_error_test',
            'status': 'failed',
            'duration_ms': 8000,
            'duration_seconds': 8.0,
            'failure_reason': 'Network error: Failed to fetch data from API endpoint',
            'environment': 'staging-webserver01',
            'failure_category': 'other'
        },
        {
            'test_name': 'element_not_found_test',
            'status': 'failed',
            'duration_ms': 12000,
            'duration_seconds': 12.0,
            'failure_reason': 'Element with selector .submit-button not found',
            'environment': 'prod-loadbalancer',
            'failure_category': 'unknown'
        },
        {
            'test_name': 'data_validation_test',
            'status': 'failed',
            'duration_ms': 3000,
            'duration_seconds': 3.0,
            'failure_reason': 'Expected value "John" but got "Jane"',
            'environment': 'dev-database-primary',
            'failure_category': 'unknown'
        },
        {
            'test_name': 'successful_checkout_test',
            'status': 'passed',
            'duration_ms': 4500,
            'duration_seconds': 4.5,
            'failure_reason': None,
            'environment': 'qa-server-west',
            'failure_category': None
        },
        {
            'test_name': 'performance_load_test',
            'status': 'failed',
            'duration_ms': 45000,
            'duration_seconds': 45.0,
            'failure_reason': 'Performance threshold exceeded: Response time 45s > 30s limit',
            'environment': 'staging-performance-env',
            'failure_category': 'unknown'
        },
        {
            'test_name': 'fast_unit_test',
            'status': 'passed',
            'duration_ms': 800,
            'duration_seconds': 0.8,
            'failure_reason': None,
            'environment': 'dev-unittest-runner',
            'failure_category': None
        }
    ]
    
    return sample_tests

def test_enhanced_analyzer():
    """Test the enhanced analyzer with sample data"""
    
    try:
        from integrated_analyzer import IntegratedTestAnalyzer
        
        print("🧪 Testing Enhanced Test Analyzer")
        print("=" * 50)
        
        # Create sample test data
        sample_tests = create_sample_test_data()
        print(f"📋 Created {len(sample_tests)} sample test results")
        
        # Initialize integrated analyzer
        analyzer = IntegratedTestAnalyzer()
        print("✅ Initialized IntegratedTestAnalyzer")
        
        # Run enhanced analysis
        print("\n🚀 Running enhanced analysis...")
        enhanced_result = analyzer.analyze_test_data(sample_tests)
        
        if 'error' in enhanced_result:
            print(f"❌ Analysis failed: {enhanced_result['error']}")
            return False
        
        # Display results
        print("\n📊 Enhanced Analysis Results:")
        print("-" * 40)
        
        # Show improvements
        improvements = enhanced_result.get('improvements', {})
        cat_improvement = improvements.get('categorization_improvement', {})
        
        print(f"✨ Categorization Improvements:")
        print(f"   Unknown Before: {cat_improvement.get('unknown_before', 0)}")
        print(f"   Unknown After: {cat_improvement.get('unknown_after', 0)}")
        print(f"   Improvement Count: {cat_improvement.get('improvement_count', 0)}")
        print(f"   Improvement %: {cat_improvement.get('improvement_percentage', 0):.1f}%")
        
        # Show enhanced categorization
        summary = enhanced_result.get('summary', {})
        enhanced_cat = summary.get('enhanced_categorization', {})
        category_dist = enhanced_cat.get('category_distribution', {})
        
        print(f"\n🏷️ Enhanced Categories Found:")
        for category, count in category_dist.items():
            print(f"   - {category.replace('_', ' ').title()}: {count} tests")
        
        # Show environment mapping
        env_analysis = summary.get('environment_analysis', {})
        env_dist = env_analysis.get('environment_distribution', {})
        
        print(f"\n🌍 Environment Mapping:")
        for env, count in env_dist.items():
            print(f"   - {env.capitalize()}: {count} tests")
        
        # Show performance insights
        perf_analysis = enhanced_result.get('performance_analysis', {})
        if perf_analysis and 'error' not in perf_analysis:
            print(f"\n⚡ Performance Analysis:")
            print(f"   Average Duration: {perf_analysis.get('average_duration_seconds', 0):.1f}s")
            print(f"   Total Execution Time: {perf_analysis.get('total_execution_time_minutes', 0):.1f}min")
            
            perf_dist = perf_analysis.get('performance_percentages', {})
            print(f"   Fast Tests (<5s): {perf_dist.get('fast', 0):.1f}%")
            print(f"   Slow Tests (>30s): {perf_dist.get('slow', 0) + perf_dist.get('very_slow', 0):.1f}%")
        
        # Show top insights
        failure_insights = summary.get('failure_insights', {})
        top_hints = failure_insights.get('top_failure_hints', [])
        
        if top_hints:
            print(f"\n💡 Top Actionable Insights:")
            for i, hint in enumerate(top_hints[:3], 1):
                print(f"   {i}. {hint['test_name']} ({hint['category']}):")
                print(f"      {hint['hint']}")
        
        # Generate comprehensive report
        print(f"\n📄 Generating comprehensive report...")
        report = analyzer.generate_enhanced_report(enhanced_result)
        
        # Save test results
        output_dir = "test_enhanced_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save report
        report_file = os.path.join(output_dir, f"test_enhanced_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save analysis data
        json_file = os.path.join(output_dir, f"test_enhanced_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_result, f, indent=2, default=str)
        
        print(f"✅ Test completed successfully!")
        print(f"📁 Results saved to: {output_dir}")
        print(f"   - Report: {report_file}")
        print(f"   - Data: {json_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual components of the enhanced analyzer"""
    
    print("\n🔧 Testing Individual Components")
    print("=" * 50)
    
    try:
        # Test Enhanced Test Analyzer
        from enhanced_test_analyzer import EnhancedTestAnalyzer
        enhanced_analyzer = EnhancedTestAnalyzer()
        
        sample_test = {
            'test_name': 'auth_failure_test',
            'status': 'failed',
            'failure_reason': 'Authentication failed: Invalid credentials',
            'environment': 'dev-linuxaa8d0014O1',
            'failure_category': 'unknown'
        }
        
        enhanced_test = enhanced_analyzer.enhance_test_result(sample_test)
        print(f"✅ EnhancedTestAnalyzer: {enhanced_test.get('failure_category', 'unknown')} -> {enhanced_test.get('failure_hint', 'No hint')}")
        
        # Test Performance Analyzer
        from performance_analyzer import PerformanceAnalyzer
        perf_analyzer = PerformanceAnalyzer()
        
        sample_tests = create_sample_test_data()
        perf_analysis = perf_analyzer.analyze_test_durations(sample_tests)
        print(f"✅ PerformanceAnalyzer: Analyzed {perf_analysis.get('total_tests_analyzed', 0)} tests")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 Enhanced Test Analyzer Validation")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test individual components
    component_test_passed = test_individual_components()
    
    # Test integrated analyzer
    integration_test_passed = test_enhanced_analyzer()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Component Tests: {'✅ PASSED' if component_test_passed else '❌ FAILED'}")
    print(f"   Integration Tests: {'✅ PASSED' if integration_test_passed else '❌ FAILED'}")
    
    if component_test_passed and integration_test_passed:
        print("\n🎉 All tests passed! Enhanced analyzer is ready for use.")
        print("\n💡 Next steps:")
        print("   1. Run with real test data: python analyze.py --input your_test_directory")
        print("   2. Compare results with previous analyzer")
        print("   3. Validate categorization improvements")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)