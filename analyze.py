#!/usr/bin/env python3
"""
Simple launcher for local test analysis
Runs without complex module imports
"""
import os
import sys

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def main():
    """Main entry point for local analysis"""
    try:
        # Import and run the local analyzer
        from utils.local_analyzer import main as local_main
        local_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Please run the setup script first: .\\scripts\\setup.ps1")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()