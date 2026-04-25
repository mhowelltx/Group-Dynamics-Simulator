@echo off
setlocal

set VENV_DIR=.venv

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. Is Python installed?
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"

echo Installing / verifying dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo.
echo Starting Group Dynamics Simulator at http://localhost:8000
echo Press Ctrl+C to stop.
echo.
python run.py

endlocal
