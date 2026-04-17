@echo off
setlocal enabledelayedexpansion
title AI HR System - Launcher
color 0A

echo ============================================
echo    AI HR System - One-Click Launcher
echo ============================================
echo.

:: -------------------------------------------
:: 1. Check MySQL
:: -------------------------------------------
echo [1/5] Checking MySQL...

set "MYSQL_CMD="
if exist "C:\xampp\mysql\bin\mysql.exe" (
    set "MYSQL_CMD=C:\xampp\mysql\bin\mysql.exe"
) else (
    where mysql >nul 2>&1
    if !errorlevel!==0 set "MYSQL_CMD=mysql"
)

if "%MYSQL_CMD%"=="" (
    color 0C
    echo    [ERROR] mysql.exe not found!
    echo    Install XAMPP or add MySQL to PATH.
    echo    Expected: C:\xampp\mysql\bin\mysql.exe
    pause
    exit /b 1
)

"%MYSQL_CMD%" -u root --connect-timeout=3 -e "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo    [WARN] MySQL not running. Trying to start...
    if exist "C:\xampp\mysql\bin\mysqld.exe" (
        start "" "C:\xampp\mysql\bin\mysqld.exe" --defaults-file="C:\xampp\mysql\bin\my.ini"
        timeout /t 5 /nobreak >nul
        "%MYSQL_CMD%" -u root --connect-timeout=3 -e "SELECT 1;" >nul 2>&1
    )
    if !errorlevel! neq 0 (
        color 0C
        echo    [ERROR] MySQL is not running.
        echo    Open XAMPP Control Panel and start MySQL.
        pause
        exit /b 1
    )
)
echo    [OK] MySQL is running
echo.

:: -------------------------------------------
:: 2. Create database
:: -------------------------------------------
echo [2/5] Creating database if needed...
"%MYSQL_CMD%" -u root -e "CREATE DATABASE IF NOT EXISTS hr_agentfactory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo    [ERROR] Failed to create database.
    pause
    exit /b 1
)
echo    [OK] Database 'hr_agentfactory' ready
echo.

:: -------------------------------------------
:: 3. Detect Python (try python, py, python3)
:: -------------------------------------------
echo [3/5] Checking dependencies...

set "PYTHON_CMD="
set "PYTHON_VER="

:: Try 'python' - verify it's real (not Windows Store stub)
python -c "import sys; sys.exit(0)" >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=python"
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PYTHON_VER=%%v"
)

:: Try 'py' launcher
if "%PYTHON_CMD%"=="" (
    py -c "import sys; sys.exit(0)" >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_CMD=py"
        for /f "tokens=2 delims= " %%v in ('py --version 2^>^&1') do set "PYTHON_VER=%%v"
    )
)

:: Try 'python3'
if "%PYTHON_CMD%"=="" (
    python3 -c "import sys; sys.exit(0)" >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_CMD=python3"
        for /f "tokens=2 delims= " %%v in ('python3 --version 2^>^&1') do set "PYTHON_VER=%%v"
    )
)

if "%PYTHON_CMD%"=="" (
    color 0C
    echo    [ERROR] Python not found!
    echo.
    echo    Option 1: Install Python 3.11+ from python.org
    echo             CHECK "Add Python to PATH" during install
    echo.
    echo    Option 2: Run fix-python.bat for detailed diagnostics
    pause
    exit /b 1
)
echo    [OK] Python %PYTHON_VER% (%PYTHON_CMD%)

:: Verify pip works
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo    [WARN] pip not found. Attempting fix...
    %PYTHON_CMD% -m ensurepip --upgrade >nul 2>&1
    %PYTHON_CMD% -m pip --version >nul 2>&1
    if !errorlevel! neq 0 (
        color 0C
        echo    [ERROR] pip is missing and cannot be installed.
        echo    Run fix-python.bat to resolve this.
        pause
        exit /b 1
    )
)
echo    [OK] pip is available

:: Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo    [ERROR] Node.js not found.
    echo    Install Node.js 18+ from nodejs.org
    pause
    exit /b 1
)
for /f "tokens=1 delims=" %%v in ('node --version 2^>^&1') do echo    [OK] Node.js %%v
echo.

:: -------------------------------------------
:: 4. Install dependencies if needed
:: -------------------------------------------
echo [4/5] Checking project dependencies...

:: --- Backend ---
cd /d "%~dp0backend"

if not exist "venv\Scripts\activate.bat" (
    echo    Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv 2>&1
    if !errorlevel! neq 0 (
        echo    [WARN] venv failed, trying virtualenv...
        %PYTHON_CMD% -m pip install virtualenv --quiet 2>nul
        %PYTHON_CMD% -m virtualenv venv 2>&1
        if !errorlevel! neq 0 (
            color 0C
            echo    [ERROR] Cannot create virtual environment.
            echo    Run fix-python.bat for diagnostics.
            pause
            exit /b 1
        )
    )
    echo    [OK] Virtual environment created
)

:: Install packages if fastapi not found in venv
if not exist "venv\Lib\site-packages\fastapi" (
    echo    Installing backend dependencies (first run, ~1-2 min)...
    call venv\Scripts\activate.bat
    python -m pip install -r requirements.txt --quiet 2>&1
    if !errorlevel! neq 0 (
        color 0E
        echo    [WARN] Some packages may have failed.
        echo    Run fix-python.bat to retry individually.
    )
    call deactivate
)

:: Quick sanity check: can we import uvicorn?
call venv\Scripts\activate.bat
python -c "import uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo    [WARN] uvicorn missing. Installing...
    python -m pip install uvicorn[standard] --quiet 2>&1
    python -c "import uvicorn" >nul 2>&1
    if !errorlevel! neq 0 (
        color 0C
        call deactivate
        echo    [ERROR] uvicorn won't install. Run fix-python.bat
        pause
        exit /b 1
    )
)
call deactivate
echo    [OK] Backend dependencies ready

:: --- Frontend ---
cd /d "%~dp0frontend"
if not exist "node_modules\.package-lock.json" (
    echo    Installing frontend dependencies...
    call npm install --silent 2>&1
)
echo    [OK] Frontend dependencies ready
echo.

:: -------------------------------------------
:: 5. Launch everything
:: -------------------------------------------
echo [5/5] Starting servers...
echo.

:: Start backend in new terminal
cd /d "%~dp0backend"
start "AI HR Backend" cmd /k "title AI HR Backend (port 8000) && color 0B && call venv\Scripts\activate.bat && echo. && echo  Starting FastAPI on http://localhost:8000 && echo  API docs: http://localhost:8000/docs && echo. && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

:: Start frontend in new terminal
cd /d "%~dp0frontend"
start "AI HR Frontend" cmd /k "title AI HR Frontend (port 5173) && color 0D && echo. && echo  Starting React on http://localhost:5173 && echo. && npm run dev"

echo    Waiting for servers...
timeout /t 5 /nobreak >nul

:: Open browser
start "" "http://localhost:5173"

echo.
echo ============================================
echo    All systems launched!
echo ============================================
echo.
echo    Frontend:  http://localhost:5173
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo    To stop: close the Backend and Frontend
echo    terminal windows.
echo ============================================
echo.
pause
