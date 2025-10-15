@echo off
cd /d "%~dp0"
test_analysis_env\Scripts\python.exe -m src.core.automated_scheduler %*
pause
