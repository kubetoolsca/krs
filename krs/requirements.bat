@echo off
REM Ensure we're in the script's directory
cd /d %~dp0

REM Install the requirements
pip install -r krs/requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121
if %errorlevel% neq 0 (
    echo Error occurred during pip install. Exiting.
    exit /b %errorlevel%
)

REM Run the printdependency script
python krs/printdependency.py
if %errorlevel% neq 0 (
    echo Error occurred during script execution. Exiting.
    exit /b %errorlevel%
)

echo Requirements installation and script execution completed successfully.
