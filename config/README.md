# Configuration Guide

This directory contains all configuration files for the Test Log Analysis System.

## 📄 Configuration Files

### **quality_gates.json**
Defines quality thresholds for different environments.

```json
{
  "production": {
    "failure_rate_threshold": 5.0,    // Max 5% failure rate
    "high_priority_threshold": 3,     // Max 3 high priority failures
    "pass_rate_threshold": 95.0       // Min 95% pass rate
  },
  "staging": {
    "failure_rate_threshold": 15.0,   // Max 15% failure rate
    "high_priority_threshold": 7,     // Max 7 high priority failures  
    "pass_rate_threshold": 80.0       // Min 80% pass rate
  }
}
```

### **scheduler_config.json**
Controls automated daily execution settings.

```json
{
  "schedule_time": "09:00",           // Daily execution time (24hr format)
  "timezone": "UTC",                 // Timezone for scheduling
  "azure": {
    "container_name": "test-results", // Azure container name
    "max_files_per_run": 100         // Limit files processed per run
  },
  "notifications": {
    "channels": ["email", "slack"],   // Notification channels
    "daily_summary": true,           // Send daily summaries
    "immediate_alerts": true         // Send immediate failure alerts
  }
}
```

### **failure_rules.yaml**
Customizes failure categorization rules.

```yaml
failure_rules:
  authentication_error:
    keywords: ['login failed', 'unauthorized', 'token']
    priority: 'Critical'
    category: 'Authentication Error'
  
  timeout:
    keywords: ['timeout', 'timed out', 'waiting for']
    priority: 'High'
    category: 'Timeout'
```

## 🔧 Environment Configuration

### **.env** (Create in root directory)
```bash
# Azure Blob Storage
AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_CONTAINER_NAME=test-results

# Email Notifications  
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=notifications@company.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=qa-team@company.com,dev-leads@company.com

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/...

# Teams Integration
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

# Quality Gate Defaults
MAX_FAILURE_RATE=15.0
MAX_HIGH_PRIORITY_FAILURES=7
MIN_PASS_RATE=80.0
```

## 📝 Configuration Tips

### **Environment-Specific Settings**
- Use different quality gates for prod/staging/dev
- Adjust notification frequency based on environment
- Set appropriate file processing limits

### **Security Best Practices**
- Store sensitive credentials in environment variables
- Use app-specific passwords for email
- Rotate webhook URLs regularly
- Avoid committing .env files to version control

### **Performance Tuning**
- Adjust `max_files_per_run` based on processing capacity
- Set appropriate timeout values for your environment
- Configure retention policies for old reports

## 🔄 Configuration Updates

To update configuration:

1. **Edit the relevant config file**
2. **Restart the scheduler** (if running)
3. **Test changes** with `--validate-config` flag

```powershell
# Validate configuration
python -m src.core.automated_scheduler --validate-config

# Test notifications
python -m src.core.automated_scheduler --test-notifications
```