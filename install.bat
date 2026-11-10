@echo off
REM LAE Installation Script for Windows

echo ========================================
echo LAE AI Assistant - Installation Script
echo ========================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed successfully!
echo.

REM Run validation test
echo Running validation test...
echo.
python test_installation.py

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo To run LAE with hotkey (Alt+Space):
echo   python main.py --hotkey
echo.
echo Or use CLI mode:
echo   python main.py open google.com
echo   python main.py search "python tutorials"
echo   python main.py run chrome
echo.
pause