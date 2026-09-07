@echo off
title ClipVein Launcher
cd /d "%~dp0"

echo.
echo ==================================================
echo    CLIPVEIN - install and run
echo ==================================================
echo.

REM ---- find a REAL python (ignore Microsoft Store stub) ----
set "PY="

REM 1) the py launcher is the most reliable if present
py -3 --version >nul 2>&1 && set "PY=py -3"

REM 2) real python.exe actually runs and prints a version
if not defined PY (
    for /f "delims=" %%v in ('python --version 2^>nul') do set "PY=python"
)

REM 3) common install locations, in case PATH is not set
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
if not defined PY if exist "C:\Python312\python.exe" set "PY=C:\Python312\python.exe"

if not defined PY (
    echo Python is NOT installed on this PC.
    echo.
    echo Do this:
    echo   1. Download Python from:
    echo      https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe
    echo   2. Run it. On the FIRST screen tick  "Add python.exe to PATH".
    echo   3. Click "Install Now".
    echo   4. Then run THIS file again.
    echo.
    echo Opening the download page for you now...
    start "" "https://www.python.org/downloads/"
    echo.
    pause
    exit /b 1
)

echo Using Python:
%PY% --version
echo.

echo Installing libraries (first run can take a few minutes)...
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Could not install libraries. Send me the text above.
    echo.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo    Starting ClipVein...
echo ==================================================
echo.
%PY% -m clipvein
if errorlevel 1 (
    echo.
    echo [ERROR] The app failed to start. Send me the text above.
    echo.
    pause
    exit /b 1
)

echo.
echo App closed. Press any key to exit.
pause >nul
