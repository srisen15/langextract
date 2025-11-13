# 📁 Project Structure

## Overview

This document describes the organized folder structure of the LangExtract test analysis system.

## Root Directory

```
LangExtract/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.template                # Environment template
├── 📄 .gitignore                   # Git ignore rules
│
├── 📄 analyze_tests.py             # 🎯 MAIN ENTRY POINT - Simple analyzer
├── 📄 analyze.py                   # Alternative launcher
│
├── 📂 src/                         # Source code
│   ├── 📂 core/                    # Core analysis engine
│   │   ├── test_log_analyzer.py
│   │   └── automated_scheduler.py
│   ├── 📂 integrations/            # External integrations
│   │   ├── azure_blob_analyzer.py
│   │   └── enhanced_ci_integration.py
│   └── 📂 utils/                   # Utility modules
│       ├── enhanced_analyzer.py    # Enhanced categorization engine
│       ├── local_analyzer.py
│       └── local_analyzer_enhanced.py
│
├── 📂 docs/                        # Documentation
│   ├── 📂 guides/                  # User guides
│   │   ├── HOW_TO_USE.md          # Main usage guide
│   │   ├── QUICKSTART.md          # 5-minute quick start
│   │   └── EMAIL_GUIDE.md         # Email reporting guide
│   ├── 📂 configuration/          # Configuration docs
│   │   ├── config.yaml            # Main configuration file
│   │   └── CONFIGURATION_GUIDE.md # Configuration reference
│   ├── STRUCTURE.md               # This file
│   ├── ENHANCED_401_CATEGORIZATION.md
│   ├── ENHANCED_ANALYSIS_SUMMARY.md
│   └── README.md                  # Extended documentation
│
├── 📂 config/                      # Configuration files
│   ├── quality_gates.json
│   ├── scheduler_config.json
│   └── failure_rules.yaml
│
├── 📂 demos/                       # Demo and example scripts
│   ├── demo_401_enhancement.py
│   ├── demo_comprehensive_enhancement.py
│   └── test_*.py                  # Test/demo scripts
│
├── 📂 test_data/                   # Sample test data
│   ├── real_401_example.json
│   ├── real_403_example.json
│   └── sample_*.json
│
├── 📂 scripts/                     # Setup and utility scripts
│   ├── setup.ps1                  # Windows setup
│   ├── setup.sh                   # Linux/Mac setup
│   └── analyze_local.bat          # Quick analysis script
│
├── 📂 output/                      # Generated outputs (git-ignored)
│   ├── 📂 reports/                # Analysis reports
│   └── 📂 logs/                   # System logs
│
├── 📂 samples/                     # Sample files
└── 📂 test_analysis_env/          # Virtual environment (git-ignored)
```

## Key Directories

### `/src` - Source Code
- **`core/`**: Core analysis engine and schedulers
- **`integrations/`**: Azure, CI/CD, and external integrations
- **`utils/`**: Utility modules and enhanced analyzers

### `/docs` - Documentation
- **`guides/`**: User-facing guides (how-to, quickstart, email)
- **`configuration/`**: Configuration files and reference
- **Root**: Technical documentation and feature summaries

### `/demos` - Examples and Tests
- Demo scripts showing enhanced features
- Test scripts for validation
- Examples of 401/403 categorization

### `/test_data` - Sample Data
- Real-world test examples
- Sample JSON test results
- Used by demos and tests

### `/config` - Configuration
- Quality gates configuration
- Scheduler settings
- Failure categorization rules

### `/output` - Generated Files (Ignored by Git)
- Analysis reports (HTML, JSON, Markdown, Text)
- System logs
- Temporary files

## Quick Reference

### Main Entry Points
1. **`analyze_tests.py`** - Primary analyzer (recommended)
2. **`analyze.py`** - Alternative launcher
3. **`src/utils/local_analyzer_enhanced.py`** - Direct enhanced analysis

### Configuration
- Main config: `docs/configuration/config.yaml`
- Quality gates: `config/quality_gates.json`
- Scheduler: `config/scheduler_config.json`

### Documentation
- Quick Start: `docs/guides/QUICKSTART.md`
- Full Guide: `docs/guides/HOW_TO_USE.md`
- Email Guide: `docs/guides/EMAIL_GUIDE.md`
- Config Guide: `docs/configuration/CONFIGURATION_GUIDE.md`

### Examples
- 401 Demo: `demos/demo_401_enhancement.py`
- Comprehensive: `demos/demo_comprehensive_enhancement.py`

## File Organization Principles

1. **User Files** (root): Main entry points users interact with
2. **Source Code** (`src/`): Internal implementation
3. **Documentation** (`docs/`): All guides and references
4. **Configuration** (`config/`, `docs/configuration/`): Settings
5. **Examples** (`demos/`, `test_data/`): Learning resources
6. **Generated** (`output/`): Temporary/generated files (git-ignored)

## Migration Notes

Recent reorganization (Nov 2025):
- Moved user guides → `docs/guides/`
- Moved config files → `docs/configuration/`
- Moved demos → `demos/`
- Moved technical docs → `docs/`
- Added `enhanced_analyzer.py` to `src/utils/`

All file paths in code have been updated to reflect new structure.
