"""
Quick analysis script for the test execution log
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from test_log_analyzer import TestLogExtractor

def analyze_test_log():
    """Analyze the specific test log file"""
    json_file = r"c:\Users\senthil.vivekanandan\Downloads\112048174313a20f.json"
    
    print("🔍 Analyzing Playwright Test Execution Log...")
    print("=" * 60)
    
    extractor = TestLogExtractor(json_file)
    
    # Generate and display the report
    report = extractor.generate_test_report()
    print(report)
    
    # Additional failure analysis
    print("\n" + "=" * 60)
    print("🚨 DETAILED FAILURE ANALYSIS")
    print("=" * 60)
    
    failure_context = extractor.extract_failure_context()
    if failure_context['is_failed']:
        print(f"❌ **Test Failed**: {failure_context['failure_reason']}")
        print(f"📍 **Location**: {failure_context['failure_location']}")
        print(f"🎯 **Expected**: '{failure_context['expected_vs_actual']['expected']}'")
        print(f"📄 **Actual**: '{failure_context['expected_vs_actual']['actual']}'")
        
        print("\n📋 **Steps Leading to Failure**:")
        for i, step in enumerate(failure_context['context_steps']):
            status_icon = "✅" if step['status'] == 'passed' else "❌" if step['status'] == 'failed' else "⏳"
            duration = f"({step['duration_ms']}ms)" if step['duration_ms'] > 0 else ""
            print(f"  {i+1}. {status_icon} {step['name']} {duration}")
    
    # API calls summary
    print("\n" + "=" * 60)
    print("🌐 API CALLS SUMMARY")
    print("=" * 60)
    
    api_calls = extractor.extract_api_calls()
    for call in api_calls:
        status_icon = "✅" if call['status'] == 'passed' else "❌"
        print(f"{status_icon} {call['method']} {call['endpoint']} - {call['duration_ms']}ms")
    
    print(f"\n📊 **Total API Calls**: {len(api_calls)}")
    
    # Performance insights
    print("\n" + "=" * 60)
    print("⚡ PERFORMANCE INSIGHTS")
    print("=" * 60)
    
    timing = extractor.extract_timing_analysis()
    print(f"⏱️  **Total Test Duration**: {timing['total_duration_seconds']:.2f} seconds")
    print(f"📈 **Average Step Duration**: {timing['average_step_duration_ms']:.0f}ms")
    print(f"🔢 **Total Steps Executed**: {timing['total_steps']}")
    
    print("\n🐌 **Slowest Operations**:")
    for i, step in enumerate(timing['slowest_steps'][:5], 1):
        print(f"  {i}. {step['name'][:60]}... - {step['duration_seconds']:.2f}s")

if __name__ == "__main__":
    analyze_test_log()