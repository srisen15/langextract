@echo off
echo Testing Test Log Analysis System...
cd /d "%~dp0"
echo.
echo Testing basic functionality...
test_analysis_env\Scripts\python.exe -m src.core.automated_scheduler --run-now
echo.
echo Tests completed!
pause
