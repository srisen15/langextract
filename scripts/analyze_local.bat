@echo off
echo 🔍 Local Test Log Analyzer - Quick Run
echo ========================================
cd /d "%~dp0\.."

REM Check if virtual environment exists
if not exist "test_analysis_env\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo 💡 Please run scripts\setup.ps1 first
    pause
    exit /b 1
)

REM Activate virtual environment and run local analyzer
echo 📂 Analyzing local test files...
echo.

REM Default to the common test results folder if no parameter provided
set "INPUT_DIR=%~1"
if "%INPUT_DIR%"=="" (
    set "INPUT_DIR=C:\Users\%USERNAME%\Downloads\test results"
)

echo 📁 Input Directory: %INPUT_DIR%
echo 📊 Output Directory: .\output\reports
echo.

REM Run the local analyzer using the simple launcher
test_analysis_env\Scripts\python.exe analyze.py --input "%INPUT_DIR%" --verbose

echo.
echo ✅ Analysis completed!
echo 📊 Check the output\reports folder for detailed reports
echo.
pause