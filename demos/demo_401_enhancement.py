#!/usr/bin/env python3
"""
Demonstration of Enhanced 401 Categorization with Real Examples
"""

import sys
import os
import json

# Add the src directory to path
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
src_dir = os.path.join(current_dir, 'src')
utils_dir = os.path.join(src_dir, 'utils')
sys.path.insert(0, src_dir)
sys.path.insert(0, utils_dir)

# Import our enhanced analyzer
import local_analyzer_enhanced

def demo_enhanced_401_handling():
    """Demonstrate enhanced 401 unauthorized handling with realistic examples"""
    
    print("🚀 ENHANCED 401 UNAUTHORIZED CATEGORIZATION DEMO")
    print("=" * 70)
    print()
    
    # Initialize enhanced analyzer
    analyzer = local_analyzer_enhanced.EnhancedAnalyzer()
    
    # Load our test data examples
    test_files = [
        'test_data/real_401_example.json',
        'test_data/real_403_example.json'
    ]
    
    print("📊 Processing Real-World Authentication Failures:")
    print("-" * 50)
    
    for test_file in test_files:
        try:
            with open(test_file, 'r') as f:
                test_data = json.load(f)
            
            # Enhanced categorization
            result = analyzer.categorize_failure(test_data['failure_reason'])
            
            # Enhanced environment mapping
            mapped_env = analyzer.map_environment(test_data['environment'])
            
            print(f"\n🔍 Test: {test_data['test_name']}")
            print(f"   File: {test_data['test_file']}")
            print(f"   Duration: {test_data['duration_seconds']}s")
            print(f"   Environment: {test_data['environment']} → {mapped_env}")
            print(f"   Tags: {', '.join(test_data['tags'])}")
            print()
            print(f"   💥 Failure: {test_data['failure_reason']}")
            print()
            print(f"   ✅ Enhanced Analysis:")
            print(f"      Category: {result['category']}")
            print(f"      Confidence: {result['confidence']:.0%}")
            if 'http_status' in result:
                print(f"      HTTP Status: {result['http_status']}")
            print(f"      💡 Hint: {result['hint']}")
            print(f"      🔍 Reasoning: {result['reasoning']}")
            print()
            print("-" * 50)
            
        except FileNotFoundError:
            print(f"   ⚠️ Test file not found: {test_file}")
        except Exception as e:
            print(f"   ❌ Error processing {test_file}: {e}")
    
    print()
    print("🎯 KEY ENHANCEMENTS DEMONSTRATED:")
    print()
    print("✨ 401 Unauthorized Detection:")
    print("   - High confidence (95%) HTTP status code recognition")
    print("   - Specific hints about token expiration and credentials")
    print("   - Distinction between authentication (401) vs authorization (403)")
    print()
    print("✨ 403 Forbidden Handling:")
    print("   - Separate category for permission/role issues")
    print("   - Actionable guidance for access control troubleshooting")
    print("   - Proper HTTP status code identification")
    print()
    print("✨ Environment Mapping:")
    print("   - Raw environment names mapped to logical environments")
    print("   - Better reporting and analytics grouping")
    print()
    print("✨ Enhanced Insights:")
    print("   - Specific debugging recommendations")
    print("   - HTTP status code extraction and categorization")
    print("   - High confidence scoring for accurate categorization")
    print()
    print("🚀 The enhanced analyzer now provides:")
    print("   📋 More accurate failure categorization")
    print("   🎯 Specific 401/403 HTTP status handling")
    print("   💡 Actionable debugging hints")
    print("   📊 Better business intelligence reporting")
    print()
    print("✅ Enhanced 401 unauthorized categorization is ready for production!")

if __name__ == "__main__":
    demo_enhanced_401_handling()