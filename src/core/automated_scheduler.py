"""
Automated Daily Test Analysis Scheduler
Supports Azure Blob Storage, scheduled execution, and stakeholder notifications
"""

import schedule
import time
import logging
import json
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from pathlib import Path

# Handle imports with fallbacks for different execution contexts
try:
    from ..integrations.azure_blob_analyzer import AzureBlobTestAnalyzer
    from ..integrations.enhanced_ci_integration import QualityGates, export_metrics_to_file
except ImportError:
    try:
        from integrations.azure_blob_analyzer import AzureBlobTestAnalyzer
        from integrations.enhanced_ci_integration import QualityGates, export_metrics_to_file
    except ImportError:
        # Fallback - these will be imported when needed
        AzureBlobTestAnalyzer = None
        QualityGates = None
        export_metrics_to_file = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TestAnalysisScheduler:
    """Automated scheduler for daily test analysis"""

    def __init__(self, config_file: str = "scheduler_config.json"):
        """Initialize scheduler with configuration"""
        self.config = self.load_config(config_file)
        self.azure_analyzer = None

        # Initialize quality gates if available
        if QualityGates is not None:
            self.quality_gates = QualityGates(self.config.get('quality_gates_file'))
        else:
            self.quality_gates = None

        # Initialize Azure analyzer if configured and available
        if self.config.get('azure_blob') and AzureBlobTestAnalyzer is not None:
            self.azure_analyzer = AzureBlobTestAnalyzer(
                connection_string=self.config['azure_blob']['connection_string'],
                container_name=self.config['azure_blob']['container_name']
            )

    def load_config(self, config_file: str) -> dict:
        """Load scheduler configuration"""
        default_config = {
            "schedule": {
                "daily_time": "09:00",
                "timezone": "UTC",
                "days_back": 1
            },
            "azure_blob": {
                "connection_string": "",
                "container_name": "test-results",
                "blob_prefix": "test-logs/",
                "upload_reports": True
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipients": []
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel": "#test-failures"
                },
                "teams": {
                    "enabled": False,
                    "webhook_url": ""
                }
            },
            "quality_gates_file": "quality_gates.json",
            "reports": {
                "generate_html": True,
                "generate_csv": True,
                "generate_insights": True,
                "export_metrics": True
            }
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge configs (user config overrides defaults)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config file {config_file}: {e}")

        return default_config

    def run_daily_analysis(self):
        """Execute daily analysis workflow"""
        logger.info("🚀 Starting scheduled daily test analysis")

        try:
            # Run Azure Blob analysis if configured
            if self.azure_analyzer:
                results = self.run_azure_analysis()
            else:
                logger.error("❌ Azure Blob Storage not configured")
                return

            if not results or results['status'] != 'success':
                logger.error(f"❌ Analysis failed: {results}")
                self.send_failure_notification("Daily analysis failed")
                return

            # Extract metrics
            stats = results['stats']

            # Check quality gates
            if self.quality_gates is not None:
                gate_passed, gate_failures = self.quality_gates.check_gates(stats)
            else:
                gate_passed = True  # Default to passing if no gates configured
                gate_failures = []

            # Generate and send reports
            self.generate_reports(results, gate_passed, gate_failures)

            # Send notifications
            self.send_notifications(stats, gate_passed, gate_failures)

            logger.info("✅ Daily analysis completed successfully")

        except Exception as e:
            logger.error(f"❌ Error in daily analysis: {e}")
            self.send_failure_notification(f"Daily analysis error: {str(e)}")

    def run_azure_analysis(self) -> dict:
        """Run analysis on Azure Blob Storage"""
        config = self.config['azure_blob']

        return self.azure_analyzer.run_daily_analysis(
            blob_prefix=config.get('blob_prefix', ''),
            days_back=self.config['schedule']['days_back'],
            upload_results=config.get('upload_reports', True),
            cleanup_local=True
        )

    def generate_reports(self, results: dict, gate_passed: bool, gate_failures: list):
        """Generate various report formats"""
        stats = results['stats']

        # Create reports directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = Path(f"daily_reports_{timestamp}")
        reports_dir.mkdir(exist_ok=True)

        # Generate executive summary
        executive_summary = self.create_executive_summary(stats, gate_passed, gate_failures)
        summary_file = reports_dir / "executive_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(executive_summary)

        # Export metrics if configured and available
        if self.config['reports']['export_metrics'] and export_metrics_to_file is not None:
            metrics_file = reports_dir / "metrics.json"
            export_metrics_to_file(stats, str(metrics_file))

        logger.info(f"📊 Reports generated in: {reports_dir}")
        return str(reports_dir)

    def create_executive_summary(self, stats: dict, gate_passed: bool, gate_failures: list) -> str:
        """Create executive summary for stakeholders"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate quality score
        quality_score = self.calculate_quality_score(stats)

        # Determine status
        status_emoji = "✅" if gate_passed else "❌"
        status_text = "PASSED" if gate_passed else "FAILED"

        summary = f"""# Daily Test Analysis - Executive Summary
**Generated:** {timestamp}

## 🎯 Quality Status: {status_emoji} {status_text}
**Quality Score:** {quality_score}/100

## 📊 Key Metrics
- **Total Tests:** {stats['total_tests']}
- **Pass Rate:** {(stats['passed_tests'] / stats['total_tests'] * 100):.1f}%
- **Failure Rate:** {stats['failure_rate']:.1f}%
- **Tests Needing Attention:** {stats['needs_attention']}

## 🚨 Priority Breakdown
- **Critical Failures:** {stats.get('critical_failures', 0)}
- **High Priority Failures:** {stats.get('high_priority_failures', 0)}
- **Flaky Tests:** {stats.get('flaky_tests', 0)}

## 📋 Failure Categories
"""

        # Add category breakdown
        for category, count in stats.get('category_breakdown', {}).items():
            percentage = (count / stats['failed_tests'] * 100) if stats['failed_tests'] > 0 else 0
            summary += f"- **{category}:** {count} ({percentage:.1f}%)\n"

        # Add quality gate results
        if not gate_passed:
            summary += f"""
## ❌ Quality Gate Failures
"""
            for failure in gate_failures:
                summary += f"- {failure}\n"

        # Add recommendations
        summary += f"""
## 💡 Recommendations
"""
        recommendations = self.generate_recommendations(stats)
        for rec in recommendations:
            summary += f"- {rec}\n"

        return summary

    def calculate_quality_score(self, stats: dict) -> int:
        """Calculate overall quality score"""
        base_score = 100

        # Deduct points for failures
        deductions = 0
        deductions += stats.get('critical_failures', 0) * 25  # 25 points per critical
        deductions += stats.get('high_priority_failures', 0) * 10  # 10 points per high priority
        deductions += stats.get('flaky_tests', 0) * 3  # 3 points per flaky test

        # Deduct for high failure rate
        if stats['failure_rate'] > 15:
            deductions += (stats['failure_rate'] - 15) * 2

        return max(0, base_score - deductions)

    def generate_recommendations(self, stats: dict) -> list:
        """Generate actionable recommendations"""
        recommendations = []

        if stats.get('critical_failures', 0) > 0:
            recommendations.append("🚨 **URGENT:** Address critical failures immediately")

        if stats['failure_rate'] > 20:
            recommendations.append("📈 **High failure rate:** Investigate test environment stability")

        if stats.get('flaky_tests', 0) > 10:
            recommendations.append("🔄 **Flaky tests:** Review wait strategies and test data management")

        categories = stats.get('category_breakdown', {})

        if categories.get('Timeout', 0) > 3:
            recommendations.append("⏱️ **Performance:** Multiple timeout failures - investigate system performance")

        if categories.get('Authentication Error', 0) > 0:
            recommendations.append(
                "🔐 **Security:** Authentication failures detected - verify credentials and auth service")

        if categories.get('Data/State Issue', 0) > 2:
            recommendations.append("📊 **Data integrity:** Multiple data issues - review test data management")

        return recommendations

    def send_notifications(self, stats: dict, gate_passed: bool, gate_failures: list):
        """Send notifications to configured channels"""
        # Email notifications
        if self.config['notifications']['email']['enabled']:
            self.send_email_notification(stats, gate_passed, gate_failures)

        # Slack notifications
        if self.config['notifications']['slack']['enabled']:
            self.send_slack_notification(stats, gate_passed, gate_failures)

        # Teams notifications
        if self.config['notifications']['teams']['enabled']:
            self.send_teams_notification(stats, gate_passed, gate_failures)

    def send_email_notification(self, stats: dict, gate_passed: bool, gate_failures: list):
        """Send email notification"""
        try:
            config = self.config['notifications']['email']

            msg = MIMEMultipart()
            msg['From'] = config['username']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = f"Daily Test Analysis - {'✅ PASSED' if gate_passed else '❌ FAILED'}"

            # Create email body
            body = self.create_email_body(stats, gate_passed, gate_failures)
            msg.attach(MIMEText(body, 'html'))

            # Send email
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()

            logger.info("📧 Email notification sent")

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")

    def send_slack_notification(self, stats: dict, gate_passed: bool, gate_failures: list):
        """Send Slack notification"""
        try:
            config = self.config['notifications']['slack']

            status_emoji = "✅" if gate_passed else "❌"
            quality_score = self.calculate_quality_score(stats)

            message = {
                "channel": config.get('channel', '#test-failures'),
                "username": "Test Analysis Bot",
                "icon_emoji": ":robot_face:",
                "attachments": [
                    {
                        "color": "good" if gate_passed else "danger",
                        "title": f"{status_emoji} Daily Test Analysis Results",
                        "fields": [
                            {
                                "title": "Quality Score",
                                "value": f"{quality_score}/100",
                                "short": True
                            },
                            {
                                "title": "Total Tests",
                                "value": str(stats['total_tests']),
                                "short": True
                            },
                            {
                                "title": "Failure Rate",
                                "value": f"{stats['failure_rate']:.1f}%",
                                "short": True
                            },
                            {
                                "title": "High Priority",
                                "value": str(stats.get('high_priority_failures', 0)),
                                "short": True
                            }
                        ]
                    }
                ]
            }

            if not gate_passed:
                message["attachments"].append({
                    "color": "danger",
                    "title": "Quality Gate Failures",
                    "text": "\n".join([f"• {failure}" for failure in gate_failures])
                })

            response = requests.post(config['webhook_url'], json=message)
            if response.status_code == 200:
                logger.info("📱 Slack notification sent")
            else:
                logger.error(f"❌ Slack notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Failed to send Slack notification: {e}")

    def send_teams_notification(self, stats: dict, gate_passed: bool, gate_failures: list):
        """Send Microsoft Teams notification"""
        try:
            config = self.config['notifications']['teams']

            status_color = "00FF00" if gate_passed else "FF0000"
            status_text = "PASSED" if gate_passed else "FAILED"
            quality_score = self.calculate_quality_score(stats)

            message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": status_color,
                "summary": f"Daily Test Analysis - {status_text}",
                "sections": [
                    {
                        "activityTitle": f"Daily Test Analysis - {status_text}",
                        "activitySubtitle": f"Quality Score: {quality_score}/100",
                        "facts": [
                            {
                                "name": "Total Tests",
                                "value": str(stats['total_tests'])
                            },
                            {
                                "name": "Failure Rate",
                                "value": f"{stats['failure_rate']:.1f}%"
                            },
                            {
                                "name": "High Priority Failures",
                                "value": str(stats.get('high_priority_failures', 0))
                            },
                            {
                                "name": "Flaky Tests",
                                "value": str(stats.get('flaky_tests', 0))
                            }
                        ],
                        "markdown": True
                    }
                ]
            }

            if not gate_passed:
                message["sections"].append({
                    "activityTitle": "Quality Gate Failures",
                    "text": "\n".join([f"• {failure}" for failure in gate_failures])
                })

            response = requests.post(config['webhook_url'], json=message)
            if response.status_code == 200:
                logger.info("📢 Teams notification sent")
            else:
                logger.error(f"❌ Teams notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Failed to send Teams notification: {e}")

    def create_email_body(self, stats: dict, gate_passed: bool, gate_failures: list) -> str:
        """Create HTML email body"""
        status_color = "#28a745" if gate_passed else "#dc3545"
        status_text = "PASSED" if gate_passed else "FAILED"
        quality_score = self.calculate_quality_score(stats)

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: {status_color};">Daily Test Analysis - {status_text}</h2>

            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>Quality Score: {quality_score}/100</h3>
            </div>

            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">Metric</th>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">Value</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Total Tests</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{stats['total_tests']}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Pass Rate</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{(stats['passed_tests'] / stats['total_tests'] * 100):.1f}%</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Failure Rate</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{stats['failure_rate']:.1f}%</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">High Priority Failures</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{stats.get('high_priority_failures', 0)}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Flaky Tests</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{stats.get('flaky_tests', 0)}</td>
                </tr>
            </table>
        """

        if not gate_passed:
            html += f"""
            <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h4>Quality Gate Failures:</h4>
                <ul>
            """
            for failure in gate_failures:
                html += f"<li>{failure}</li>"
            html += "</ul></div>"

        html += """
        </body>
        </html>
        """

        return html

    def send_failure_notification(self, message: str):
        """Send notification when analysis itself fails"""
        try:
            # Send simple failure notification via configured channels
            if self.config['notifications']['slack']['enabled']:
                requests.post(
                    self.config['notifications']['slack']['webhook_url'],
                    json={
                        "text": f"🚨 Test Analysis System Failure: {message}",
                        "channel": self.config['notifications']['slack'].get('channel', '#test-failures')
                    }
                )

            logger.error(f"Failure notification sent: {message}")

        except Exception as e:
            logger.error(f"Failed to send failure notification: {e}")

    def start_scheduler(self):
        """Start the scheduler"""
        schedule_time = self.config['schedule']['daily_time']

        # Schedule daily analysis
        schedule.every().day.at(schedule_time).do(self.run_daily_analysis)

        logger.info(f"📅 Scheduler started - Daily analysis at {schedule_time}")
        logger.info("🔄 Scheduler running... (Press Ctrl+C to stop)")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("📴 Scheduler stopped by user")


def main():
    """Main function for scheduler"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Daily Test Analysis Scheduler")
    parser.add_argument("--config", default="scheduler_config.json", help="Configuration file path")
    parser.add_argument("--run-now", action="store_true", help="Run analysis immediately instead of scheduling")
    parser.add_argument("--test-notifications", action="store_true", help="Test notification systems")

    args = parser.parse_args()

    scheduler = TestAnalysisScheduler(args.config)

    if args.test_notifications:
        # Test notifications with dummy data
        test_stats = {
            'total_tests': 100,
            'passed_tests': 85,
            'failed_tests': 15,
            'failure_rate': 15.0,
            'high_priority_failures': 3,
            'critical_failures': 1,
            'flaky_tests': 5,
            'needs_attention': 4,
            'category_breakdown': {
                'Timeout': 2,
                'Data/State Issue': 1,
                'Authentication Error': 1
            }
        }
        scheduler.send_notifications(test_stats, False, ["Failure rate (15.0%) exceeds threshold (10.0%)"])

    elif args.run_now:
        scheduler.run_daily_analysis()
    else:
        scheduler.start_scheduler()


if __name__ == "__main__":
    main()
