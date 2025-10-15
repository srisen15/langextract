"""
Azure Blob Storage Integration for Test Log Analysis
Automatically downloads test logs from Azure Blob Storage and runs daily analysis
"""

import os
import sys
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient
import tempfile
import shutil
from pathlib import Path
import logging
from typing import List, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('azure_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AzureBlobTestAnalyzer:
    """Azure Blob Storage integration for test log analysis"""
    
    def __init__(self, connection_string: str, container_name: str, local_cache_dir: str = "./azure_cache"):
        """
        Initialize Azure Blob Storage client
        
        Args:
            connection_string: Azure Storage connection string
            container_name: Name of the container containing test logs
            local_cache_dir: Local directory to cache downloaded files
        """
        self.connection_string = connection_string
        self.container_name = container_name
        self.local_cache_dir = Path(local_cache_dir)
        self.blob_service_client = None
        
        # Create cache directory if it doesn't exist
        self.local_cache_dir.mkdir(exist_ok=True)
        
        # Initialize blob client
        self._init_blob_client()
    
    def _init_blob_client(self):
        """Initialize Azure Blob Storage client"""
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            logger.info(f"✅ Connected to Azure Blob Storage container: {self.container_name}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Azure Blob Storage: {e}")
            raise
    
    def list_test_logs(self, prefix: str = "", days_back: int = 1) -> List[str]:
        """
        List test log files in Azure Blob Storage
        
        Args:
            prefix: Blob name prefix to filter (e.g., "test-results/2025/10/")
            days_back: How many days back to look for files
            
        Returns:
            List of blob names matching criteria
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Calculate date filter
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            blob_names = []
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blobs:
                # Filter by file extension and modification date
                if (blob.name.endswith('.json') and 
                    blob.last_modified.replace(tzinfo=None) >= cutoff_date):
                    blob_names.append(blob.name)
            
            logger.info(f"📋 Found {len(blob_names)} test log files in the last {days_back} days")
            return blob_names
            
        except Exception as e:
            logger.error(f"❌ Error listing blobs: {e}")
            return []
    
    def download_test_logs(self, blob_names: List[str], force_download: bool = False) -> str:
        """
        Download test logs from Azure Blob Storage to local cache
        
        Args:
            blob_names: List of blob names to download
            force_download: Force re-download even if files exist locally
            
        Returns:
            Path to local directory containing downloaded files
        """
        if not blob_names:
            logger.warning("⚠️ No blob names provided for download")
            return str(self.local_cache_dir)
        
        # Create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_dir = self.local_cache_dir / f"daily_analysis_{timestamp}"
        download_dir.mkdir(exist_ok=True)
        
        container_client = self.blob_service_client.get_container_client(self.container_name)
        
        downloaded_count = 0
        for blob_name in blob_names:
            try:
                # Create local file path preserving blob structure
                local_file_path = download_dir / Path(blob_name).name
                
                # Skip if file exists and not forcing download
                if local_file_path.exists() and not force_download:
                    logger.info(f"⏭️ Skipping {blob_name} (already exists)")
                    continue
                
                # Download blob
                blob_client = container_client.get_blob_client(blob_name)
                
                with open(local_file_path, "wb") as download_file:
                    blob_data = blob_client.download_blob()
                    blob_data.readinto(download_file)
                
                downloaded_count += 1
                logger.info(f"⬇️ Downloaded: {blob_name}")
                
            except Exception as e:
                logger.error(f"❌ Error downloading {blob_name}: {e}")
        
        logger.info(f"✅ Downloaded {downloaded_count} files to {download_dir}")
        return str(download_dir)
    
    def upload_reports(self, report_dir: str, upload_prefix: str = "analysis-reports/") -> List[str]:
        """
        Upload generated reports back to Azure Blob Storage
        
        Args:
            report_dir: Local directory containing reports
            upload_prefix: Blob prefix for uploaded reports
            
        Returns:
            List of uploaded blob names
        """
        report_path = Path(report_dir)
        if not report_path.exists():
            logger.warning(f"⚠️ Report directory doesn't exist: {report_dir}")
            return []
        
        container_client = self.blob_service_client.get_container_client(self.container_name)
        uploaded_files = []
        
        # Find report files
        report_files = list(report_path.glob("test_analysis_*.csv")) + \
                      list(report_path.glob("test_report_*.html")) + \
                      list(report_path.glob("actionable_insights.md"))
        
        timestamp = datetime.now().strftime("%Y/%m/%d")
        
        for report_file in report_files:
            try:
                # Create blob name with timestamp structure
                blob_name = f"{upload_prefix}{timestamp}/{report_file.name}"
                
                # Upload file
                blob_client = container_client.get_blob_client(blob_name)
                
                with open(report_file, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)
                
                uploaded_files.append(blob_name)
                logger.info(f"⬆️ Uploaded: {blob_name}")
                
            except Exception as e:
                logger.error(f"❌ Error uploading {report_file.name}: {e}")
        
        logger.info(f"✅ Uploaded {len(uploaded_files)} report files")
        return uploaded_files
    
    def run_daily_analysis(self, 
                          blob_prefix: str = "", 
                          days_back: int = 1,
                          upload_results: bool = True,
                          cleanup_local: bool = True) -> dict:
        """
        Run complete daily analysis workflow
        
        Args:
            blob_prefix: Blob name prefix to filter
            days_back: How many days back to analyze
            upload_results: Whether to upload reports back to blob storage
            cleanup_local: Whether to cleanup local files after upload
            
        Returns:
            Analysis results summary
        """
        logger.info(f"🚀 Starting daily analysis for {days_back} days back")
        
        try:
            # 1. List and download test logs
            blob_names = self.list_test_logs(blob_prefix, days_back)
            if not blob_names:
                logger.warning("⚠️ No test logs found for analysis")
                return {"status": "no_data", "message": "No test logs found"}
            
            download_dir = self.download_test_logs(blob_names)
            
            # 2. Run analysis using production_analyzer
            from production_analyzer import BatchTestAnalyzer
            
            analyzer = BatchTestAnalyzer(download_dir)
            results = analyzer.analyze_all_logs()
            
            if not results:
                logger.warning("⚠️ No valid test data found in downloaded files")
                return {"status": "no_valid_data", "message": "No valid test data found"}
            
            # 3. Generate reports
            summary = analyzer.generate_failure_summary()
            csv_file = analyzer.export_to_csv()
            html_file = analyzer.generate_html_report()
            insights = analyzer.generate_actionable_report()
            
            # Save insights to file
            insights_file = os.path.join(download_dir, "actionable_insights.md")
            with open(insights_file, 'w', encoding='utf-8') as f:
                f.write(insights)
            
            # 4. Upload reports if requested
            uploaded_files = []
            if upload_results:
                uploaded_files = self.upload_reports(download_dir)
            
            # 5. Cleanup local files if requested
            if cleanup_local and upload_results:
                shutil.rmtree(download_dir)
                logger.info(f"🧹 Cleaned up local directory: {download_dir}")
            
            # 6. Return summary
            analysis_summary = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "stats": summary,
                "files_processed": len(blob_names),
                "reports_generated": [csv_file, html_file, insights_file],
                "uploaded_reports": uploaded_files,
                "download_dir": download_dir if not cleanup_local else "cleaned_up"
            }
            
            logger.info(f"✅ Daily analysis completed successfully")
            logger.info(f"📊 Processed {len(blob_names)} files, {summary.get('failed_tests', 0)} failures found")
            
            return analysis_summary
            
        except Exception as e:
            logger.error(f"❌ Daily analysis failed: {e}")
            return {"status": "error", "message": str(e)}

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Azure Blob Storage Test Log Analyzer")
    parser.add_argument("--connection-string", required=True, help="Azure Storage connection string")
    parser.add_argument("--container", required=True, help="Blob container name")
    parser.add_argument("--prefix", default="", help="Blob name prefix filter")
    parser.add_argument("--days-back", type=int, default=1, help="Days back to analyze")
    parser.add_argument("--no-upload", action="store_true", help="Don't upload reports back to blob storage")
    parser.add_argument("--keep-local", action="store_true", help="Keep local files after analysis")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = AzureBlobTestAnalyzer(
        connection_string=args.connection_string,
        container_name=args.container
    )
    
    # Run analysis
    results = analyzer.run_daily_analysis(
        blob_prefix=args.prefix,
        days_back=args.days_back,
        upload_results=not args.no_upload,
        cleanup_local=not args.keep_local
    )
    
    # Print results
    print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    if results["status"] == "success":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()