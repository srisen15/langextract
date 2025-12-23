"""
External Integrations
=====================

Contains integrations with external systems:
- Azure Blob Storage integration for cloud-based log processing
- CI/CD platform integrations (GitHub, Azure DevOps, Jenkins, GitLab)
- Quality gates and automated status reporting
"""

from .azure_blob_analyzer import AzureBlobTestAnalyzer
from .enhanced_ci_integration import QualityGates, CIPlatformIntegration

__all__ = ['AzureBlobTestAnalyzer', 'QualityGates', 'CIPlatformIntegration']
