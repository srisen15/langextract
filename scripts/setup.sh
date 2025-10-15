#!/bin/bash
# Setup script for Test Log Analysis System

echo "🚀 Setting up Test Log Analysis System..."

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python -m venv test_analysis_env

# Activate virtual environment
source test_analysis_env/bin/activate  # Linux/Mac
# test_analysis_env\Scripts\activate  # Windows

# Install required packages
echo "📋 Installing required packages..."
pip install azure-storage-blob requests schedule python-dotenv

# Create required directories
echo "📁 Creating directories..."
mkdir -p logs reports azure_cache daily_reports

# Set up configuration files
echo "⚙️ Setting up configuration..."

# Create environment file template
cat > .env << EOF
# Azure Blob Storage Configuration
AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your_account;AccountKey=your_key;EndpointSuffix=core.windows.net
AZURE_CONTAINER_NAME=test-results

# Notification Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
TEAMS_WEBHOOK_URL=https://your-org.webhook.office.com/YOUR/TEAMS/WEBHOOK

# Email Configuration
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@company.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=qa-team@company.com,dev-leads@company.com

# Quality Gates
MAX_FAILURE_RATE=15.0
MAX_HIGH_PRIORITY_FAILURES=7
MIN_PASS_RATE=80.0
EOF

# Create systemd service for Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 Creating systemd service..."
    cat > test-analysis-scheduler.service << EOF
[Unit]
Description=Test Analysis Scheduler
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/test_analysis_env/bin
ExecStart=$(pwd)/test_analysis_env/bin/python automated_scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    echo "📄 Service file created: test-analysis-scheduler.service"
    echo "💡 To install: sudo cp test-analysis-scheduler.service /etc/systemd/system/"
    echo "💡 To enable: sudo systemctl enable test-analysis-scheduler"
    echo "💡 To start: sudo systemctl start test-analysis-scheduler"
fi

# Create Windows Task Scheduler script
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "🔧 Creating Windows Task Scheduler script..."
    cat > setup-windows-task.ps1 << 'EOF'
# PowerShell script to create Windows Scheduled Task
$TaskName = "TestAnalysisScheduler"
$TaskPath = "\"
$PythonPath = "$env:PWD\test_analysis_env\Scripts\python.exe"
$ScriptPath = "$env:PWD\automated_scheduler.py"

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath
$Trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Daily Test Log Analysis"

Write-Host "✅ Windows Scheduled Task created: $TaskName"
Write-Host "💡 Task will run daily at 9:00 AM"
EOF
    echo "📄 PowerShell script created: setup-windows-task.ps1"
    echo "💡 Run as Administrator: powershell -ExecutionPolicy Bypass -File setup-windows-task.ps1"
fi

echo ""
echo "✅ Setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Update .env file with your Azure and notification credentials"
echo "2. Update quality_gates.json with your quality thresholds"
echo "3. Update scheduler_config.json with your specific settings"
echo ""
echo "🧪 Test the system:"
echo "   python automated_scheduler.py --run-now"
echo ""
echo "🔔 Test notifications:"
echo "   python automated_scheduler.py --test-notifications"
echo ""
echo "🚀 Start scheduler:"
echo "   python automated_scheduler.py"
echo ""
echo "📊 Manual analysis:"
echo "   python enhanced_ci_integration.py --azure-connection \"\$AZURE_CONNECTION_STRING\" --azure-container \"\$AZURE_CONTAINER_NAME\""