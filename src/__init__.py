"""
Test Log Analysis System
========================

A comprehensive solution for automating test failure analysis, categorization, and reporting.
Processes Playwright test execution logs to provide actionable insights and quality metrics.

Key Features:
- 🤖 Automated Analysis: Daily processing of test logs from Azure Blob Storage
- 🏷️ Smart Categorization: 9 predefined failure categories with priority levels
- 📊 Quality Gates: Configurable thresholds with CI/CD integration
- 🔔 Multi-Channel Notifications: Email, Slack, and Teams integration
- 📈 Trend Analysis: Historical data and pattern recognition
- 🎯 Executive Reporting: Stakeholder-friendly summaries

Modules:
- core: Core analysis engine and scheduling
- integrations: Azure Blob Storage and CI/CD integrations
- utils: Local analysis and production utilities
"""

__version__ = "2.1.0"
__author__ = "Test Analysis Team"

# Core components
from .core.test_log_analyzer import TestLogExtractor, BatchTestAnalyzer
from .core.automated_scheduler import TestAnalysisScheduler

# Integrations
from .integrations.azure_blob_analyzer import AzureBlobTestAnalyzer
from .integrations.enhanced_ci_integration import QualityGates, CIPlatformIntegration

# Utilities
from .utils.local_analyzer import LocalTestAnalyzer
from .utils.production_analyzer import ProductionAnalyzer

__all__ = [
    'TestLogExtractor',
    'BatchTestAnalyzer', 
    'TestAnalysisScheduler',
    'AzureBlobTestAnalyzer',
    'QualityGates',
    'CIPlatformIntegration',
    'LocalTestAnalyzer',
    'ProductionAnalyzer'
]