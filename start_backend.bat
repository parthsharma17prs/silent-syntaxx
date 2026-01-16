@echo off
REM Hack-Vento 2K26 Backend Startup Script
echo ============================================================
echo   Hack-Vento 2K26 - Placement Portal Backend Server
echo ============================================================
echo.

cd /d "%~dp0backend"
echo Current directory: %cd%
echo.

echo Checking Python environment...
 set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
 if exist "%PYTHON_EXE%" (
	 set "PYTHON_CMD=%PYTHON_EXE%"
 ) else (
	 set "PYTHON_CMD=python"
 )
 %PYTHON_CMD% --version
echo.

echo Starting Flask server...
echo Access the application at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

 %PYTHON_CMD% app.py

pause