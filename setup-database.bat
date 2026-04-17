@echo off
title AI HR System - Database Setup
color 0B

echo ============================================
echo    AI HR System - Database Setup
echo ============================================
echo.

:: Find mysql
set "MYSQL_CMD="
if exist "C:\xampp\mysql\bin\mysql.exe" (
    set "MYSQL_CMD=C:\xampp\mysql\bin\mysql.exe"
) else (
    where mysql >nul 2>&1
    if %errorlevel%==0 (
        set "MYSQL_CMD=mysql"
    )
)

if "%MYSQL_CMD%"=="" (
    color 0C
    echo [ERROR] mysql.exe not found!
    echo         Make sure XAMPP is installed or MySQL is in PATH.
    pause
    exit /b 1
)

:: Check MySQL is running
"%MYSQL_CMD%" -u root --connect-timeout=3 -e "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] MySQL is not running!
    echo         Open XAMPP Control Panel and start MySQL first.
    pause
    exit /b 1
)

echo [1/3] MySQL connection OK
echo.

:: Create database
echo [2/3] Creating database...
"%MYSQL_CMD%" -u root -e "CREATE DATABASE IF NOT EXISTS hr_agentfactory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Failed to create database.
    pause
    exit /b 1
)
echo       Database 'hr_agentfactory' created (or already exists).
echo.

:: Show databases to confirm
echo [3/3] Verifying...
"%MYSQL_CMD%" -u root -e "SHOW DATABASES LIKE 'hr_agentfactory';"
echo.

color 0A
echo ============================================
echo    Database setup complete!
echo ============================================
echo.
echo    Database: hr_agentfactory
echo    User:     root (no password)
echo    Port:     3306
echo.
echo    Tables will be auto-created when the
echo    backend starts for the first time.
echo ============================================
echo.
pause
