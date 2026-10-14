@echo off
REM Network Monitor Launcher
REM Starts the local network monitoring web UI

echo ============================================
echo   Network Monitor - Starting...
echo   Open http://localhost:5000 in your browser
echo ============================================
echo.

cd /d "%~dp0"

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
python -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Flask...
    pip install -r requirements.txt
)

REM Start the app
echo.
echo Starting server on http://localhost:5000
echo Press Ctrl+C to stop
echo.
python app.py

pause
