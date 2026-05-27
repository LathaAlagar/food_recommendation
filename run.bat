@echo off
echo ===================================================
echo             FoodieFinds AI Launcher
echo ===================================================
echo.

:: Check if virtual environment exists, if not create it
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed and in your PATH.
        pause
        exit /b 1
    )
)

:: Activate and install/verify dependencies
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing/verifying package requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Start Flask server
echo.
echo [SUCCESS] Everything is ready! Starting FoodieFinds AI server...
echo Access the application at: http://127.0.0.1:5000
echo.
python app.py
pause
