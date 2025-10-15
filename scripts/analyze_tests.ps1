# PowerShell Script for Test Log Analysis
# Usage: .\analyze_tests.ps1 -LogDirectory "C:\path\to\logs" -OutputFormat "html"

param(
    [Parameter(Mandatory=$false)]
    [string]$LogDirectory = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$LogFile = "",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "csv", "html", "markdown")]
    [string]$OutputFormat = "all",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("critical", "high", "medium", "low", "all")]
    [string]$PriorityFilter = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$NeedsAttentionOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$Quiet,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput,
    
    [Parameter(Mandatory=$false)]
    [string]$Pattern = "*.json"
)

# Set error preference
$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Check if production_analyzer.py exists
$AnalyzerScript = Join-Path $ScriptDir "production_analyzer.py"
if (-not (Test-Path $AnalyzerScript)) {
    Write-Error "production_analyzer.py not found in $ScriptDir"
    exit 1
}

# Build command arguments
$arguments = @()

if ($LogFile) {
    $arguments += "--file", $LogFile
} else {
    $arguments += "--directory", $LogDirectory
}

$arguments += "--output-format", $OutputFormat
$arguments += "--priority-filter", $PriorityFilter
$arguments += "--pattern", $Pattern

if ($NeedsAttentionOnly) {
    $arguments += "--needs-attention-only"
}

if ($Quiet) {
    $arguments += "--quiet"
}

if ($VerboseOutput) {
    $arguments += "--verbose"
}

Write-Host "Starting Test Log Analysis..." -ForegroundColor Cyan

try {
    # Run the Python analyzer
    $result = & python $AnalyzerScript @arguments
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Analysis completed successfully!" -ForegroundColor Green
        
        # Show generated files
        if (-not $Quiet) {
            Write-Host "`nGenerated Reports:" -ForegroundColor Yellow
            
            $reportDir = if ($LogFile) { Split-Path -Parent $LogFile } else { $LogDirectory }
            
            Get-ChildItem -Path $reportDir -Filter "test_analysis_*.csv" | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 1 | 
                ForEach-Object { Write-Host "  CSV: $($_.FullName)" -ForegroundColor Gray }
            
            Get-ChildItem -Path $reportDir -Filter "test_report_*.html" | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 1 | 
                ForEach-Object { Write-Host "  HTML: $($_.FullName)" -ForegroundColor Gray }
            
            if (Test-Path (Join-Path $reportDir "actionable_insights.md")) {
                Write-Host "  Insights: $(Join-Path $reportDir "actionable_insights.md")" -ForegroundColor Gray
            }
        }
        
    } else {
        Write-Host "Analysis failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    
    # Output the result
    Write-Output $result
    
} catch {
    Write-Host "Error running analysis: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Examples and help
if ($args -contains "--help" -or $args -contains "-h") {
    Write-Host @"

USAGE EXAMPLES:

# Analyze all JSON files in current directory
.\analyze_tests.ps1

# Analyze specific directory with verbose output
.\analyze_tests.ps1 -LogDirectory "C:\TestResults" -Verbose

# Analyze single file and generate only HTML report
.\analyze_tests.ps1 -LogFile "test-result.json" -OutputFormat "html"

# Show only high priority failures
.\analyze_tests.ps1 -PriorityFilter "high" -NeedsAttentionOnly

# Quiet mode for CI/CD
.\analyze_tests.ps1 -LogDirectory ".\test-results" -Quiet -OutputFormat "csv"

PARAMETERS:
  -LogDirectory    : Directory containing test log files (default: current directory)
  -LogFile         : Single test log file to analyze
  -OutputFormat    : Report format: all, csv, html, markdown (default: all)
  -PriorityFilter  : Filter by priority: critical, high, medium, low, all (default: all)
  -NeedsAttentionOnly : Show only tests that need attention
  -Pattern         : File pattern to match (default: *.json)
  -Quiet           : Suppress console output
  -Verbose         : Verbose output

"@ -ForegroundColor Cyan
}