# PowerShell Setup Script for Windows
# Test Log Analysis System Setup

Write-Host "Setting up Test Log Analysis System..." -ForegroundColor Green

# Create virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv test_analysis_env

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\test_analysis_env\Scripts\Activate.ps1"

# Install required packages
Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create required directories
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "output\logs", "output\reports", "output\azure_cache", "output\daily_reports"

# Create environment file template from existing template
Write-Host "Setting up configuration..." -ForegroundColor Yellow
if (Test-Path ".env.template") {
    Copy-Item ".env.template" ".env"
    Write-Host "Created .env from template - please update with your credentials" -ForegroundColor Green
} else {
    # Create basic .env file
    $envContent = "# Azure Blob Storage Configuration`nAZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your_account;AccountKey=your_key;EndpointSuffix=core.windows.net`nAZURE_CONTAINER_NAME=test-results`n`n# Email Configuration`nEMAIL_USERNAME=your_email@company.com`nEMAIL_RECIPIENTS=qa-team@company.com`n`n# Quality Gates`nMAX_FAILURE_RATE=15.0`nMAX_HIGH_PRIORITY_FAILURES=7`nMIN_PASS_RATE=80.0"
    $envContent | Out-File -FilePath ".env" -Encoding utf8
}

# Create simple batch files
Write-Host "Creating batch files..." -ForegroundColor Yellow

# Scheduler batch file
$schedulerBatch = "@echo off`ncd /d `"%~dp0`"`ntest_analysis_env\Scripts\python.exe -m src.core.automated_scheduler %*`npause"
$schedulerBatch | Out-File -FilePath "run_scheduler.bat" -Encoding ascii

# Test batch file  
$testBatch = "@echo off`necho Testing Test Log Analysis System...`ncd /d `"%~dp0`"`necho.`necho Testing basic functionality...`ntest_analysis_env\Scripts\python.exe -m src.core.automated_scheduler --run-now`necho.`necho Tests completed!`npause"
$testBatch | Out-File -FilePath "test_system.bat" -Encoding ascii

Write-Host ""
Write-Host "Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update .env file with your Azure and notification credentials" -ForegroundColor White
Write-Host "2. Update config files as needed" -ForegroundColor White
Write-Host ""
Write-Host "ANALYZE LOCAL FILES:" -ForegroundColor Green
Write-Host "   .\scripts\analyze_local.bat" -ForegroundColor Yellow
Write-Host "   OR" -ForegroundColor Gray  
Write-Host "   python analyze.py --input `"C:\path\to\test\files`"" -ForegroundColor Yellow
Write-Host ""
Write-Host "Test the system:" -ForegroundColor Cyan
Write-Host "   .\test_system.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "Start scheduler:" -ForegroundColor Cyan  
Write-Host "   .\run_scheduler.bat" -ForegroundColor Yellow