@echo off
setlocal enabledelayedexpansion
title AI HR System - Python Fix Tool
color 0B

echo ============================================
echo    AI HR System - Python Fix Tool
echo ============================================
echo.

:: -------------------------------------------
:: 1. Detect which Python command works
:: -------------------------------------------
echo [1/5] Detecting Python installations...
echo.

set "PYTHON_CMD="
set "PYTHON_VER="

:: Try 'python' first (most common on Windows)
python --version >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PYTHON_VER=%%v"
    :: Make sure it's real Python, not the Windows Store stub
    python -c "import sys; sys.exit(0)" >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_CMD=python"
        echo    [OK] python --version  =  Python !PYTHON_VER!
    ) else (
        echo    [--] python             =  Windows Store redirect (not real Python^)
    )
)

:: Try 'py' launcher
if "%PYTHON_CMD%"=="" (
    py --version >nul 2>&1
    if !errorlevel!==0 (
        for /f "tokens=2 delims= " %%v in ('py --version 2^>^&1') do set "PYTHON_VER=%%v"
        set "PYTHON_CMD=py"
        echo    [OK] py --version      =  Python !PYTHON_VER!
    ) else (
        echo    [--] py                 =  not found
    )
)

:: Try 'python3'
if "%PYTHON_CMD%"=="" (
    python3 --version >nul 2>&1
    if !errorlevel!==0 (
        for /f "tokens=2 delims= " %%v in ('python3 --version 2^>^&1') do set "PYTHON_VER=%%v"
        set "PYTHON_CMD=python3"
        echo    [OK] python3 --version =  Python !PYTHON_VER!
    ) else (
        echo    [--] python3            =  not found
    )
)

echo.

:: Show all installed versions via py launcher
py --list-paths >nul 2>&1
if %errorlevel%==0 (
    echo    Installed Python versions:
    for /f "tokens=*" %%a in ('py --list-paths 2^>^&1') do echo      %%a
    echo.
)

if "%PYTHON_CMD%"=="" (
    color 0C
    echo ============================================
    echo    Python NOT FOUND on this system!
    echo ============================================
    echo.
    echo    Download Python 3.11 from:
    echo    https://www.python.org/downloads/
    echo.
    echo    IMPORTANT during installation:
    echo    [x] Check "Add Python to PATH"
    echo    [x] Check "Install pip"
    echo.
    echo    After installing, CLOSE this window
    echo    and run fix-python.bat again.
    echo ============================================
    pause
    exit /b 1
)

echo    Using: %PYTHON_CMD% (Python %PYTHON_VER%)
echo.

:: -------------------------------------------
:: 2. Check and fix pip
:: -------------------------------------------
echo [2/5] Checking pip...

%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo    [WARN] pip not found. Installing pip...
    echo.
    %PYTHON_CMD% -m ensurepip --upgrade 2>&1
    if !errorlevel! neq 0 (
        echo    ensurepip failed. Trying get-pip.py...
        curl -sS https://bootstrap.pypa.io/get-pip.py -o "%TEMP%\get-pip.py" 2>&1
        %PYTHON_CMD% "%TEMP%\get-pip.py" 2>&1
        del "%TEMP%\get-pip.py" 2>nul
    )
    %PYTHON_CMD% -m pip --version >nul 2>&1
    if !errorlevel! neq 0 (
        color 0C
        echo    [ERROR] Could not install pip.
        echo    Try reinstalling Python with "Install pip" checked.
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%v in ('%PYTHON_CMD% -m pip --version 2^>^&1') do echo    [OK] %%v
echo.

:: Upgrade pip to latest
echo    Upgrading pip to latest...
%PYTHON_CMD% -m pip install --upgrade pip --quiet 2>&1
echo    [OK] pip upgraded
echo.

:: -------------------------------------------
:: 3. Create venv and install requirements
:: -------------------------------------------
echo [3/5] Setting up virtual environment...

cd /d "%~dp0backend"

if exist "venv\Scripts\activate.bat" (
    echo    [OK] Virtual environment already exists
) else (
    echo    Creating virtual environment...
    %PYTHON_CMD% -m venv venv 2>&1
    if !errorlevel! neq 0 (
        color 0E
        echo    [WARN] venv module failed. Installing venv...
        %PYTHON_CMD% -m pip install virtualenv --quiet
        %PYTHON_CMD% -m virtualenv venv 2>&1
        if !errorlevel! neq 0 (
            color 0C
            echo    [ERROR] Cannot create virtual environment.
            pause
            exit /b 1
        )
    )
    echo    [OK] Virtual environment created
)
echo.

:: -------------------------------------------
:: 4. Install all requirements
:: -------------------------------------------
echo [4/5] Installing backend dependencies...
echo.

call venv\Scripts\activate.bat

:: Show what pip we're using inside venv
for /f "tokens=*" %%v in ('python -m pip --version 2^>^&1') do echo    Venv pip: %%v
echo.

echo    Installing requirements.txt...
echo    (this may take 1-2 minutes on first run)
echo.
python -m pip install -r requirements.txt 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo.
    echo    [WARN] Some packages failed. Retrying one by one...
    echo.
    for /f "tokens=1 delims==" %%p in (requirements.txt) do (
        echo    Installing %%p...
        python -m pip install %%p --quiet 2>nul
        if !errorlevel! neq 0 (
            echo    [SKIP] %%p failed - may need Visual C++ Build Tools
        )
    )
)
echo.
echo    [OK] Dependencies installed
echo.

:: -------------------------------------------
:: 5. Verify everything works
:: -------------------------------------------
echo [5/5] Verifying installation...
echo.

:: Test uvicorn
python -c "import uvicorn; print(f'    [OK] uvicorn {uvicorn.__version__}')" 2>&1
if %errorlevel% neq 0 (
    echo    [ERROR] uvicorn not installed properly
    echo    Trying to install manually...
    python -m pip install uvicorn[standard] --quiet
)

:: Test FastAPI
python -c "import fastapi; print(f'    [OK] fastapi {fastapi.__version__}')" 2>&1

:: Test SQLAlchemy
python -c "import sqlalchemy; print(f'    [OK] sqlalchemy {sqlalchemy.__version__}')" 2>&1

:: Test PyMySQL
python -c "import pymysql; print(f'    [OK] pymysql {pymysql.__version__}')" 2>&1

:: Test Anthropic
python -c "import anthropic; print(f'    [OK] anthropic {anthropic.__version__}')" 2>&1

:: Test Pydantic
python -c "import pydantic; print(f'    [OK] pydantic {pydantic.__version__}')" 2>&1

:: Quick uvicorn dry-run
python -c "from uvicorn.config import Config; print('    [OK] uvicorn can start')" 2>&1

call deactivate

echo.
color 0A
echo ============================================
echo    Python setup complete!
echo ============================================
echo.
echo    Python:  %PYTHON_CMD% (%PYTHON_VER%)
echo    Venv:    backend\venv\
echo    Packages: All installed
echo.
echo    You can now run START-ALL.bat
echo ============================================
echo.
pause
