@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   Nexus - High-Speed Media Ingest Setup
echo ===================================================

:: Check for Python in PATH or Local AppData
set "PYTHON_CMD=python"
python --version >nul 2>&1
if !errorlevel! neq 0 (
    :: Check if installed in default Local AppData path (Python 3.11)
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    if not exist "!PYTHON_CMD!" (
        echo [INFO] Python is not detected on this system.
        echo [INFO] Attempting to download and install Python 3.11.9...
        
        set "PYTHON_VERSION=3.11.9"
        set "INSTALLER_NAME=python-3.11.9-amd64.exe"
        set "DOWNLOAD_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        set "INSTALL_DIR=%LOCALAPPDATA%\Programs\Python\Python311"
        
        echo [INFO] Downloading Python 3.11.9 installer...
        powershell -Command "Invoke-WebRequest -Uri '!DOWNLOAD_URL!' -OutFile '%TEMP%\!INSTALLER_NAME!'"
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to download Python installer.
            pause
            exit /b 1
        )
        
        echo [INFO] Installing Python 3.11.9 silently to "!INSTALL_DIR!"...
        echo [INFO] (This may take a moment, please wait...)
        "%TEMP%\!INSTALLER_NAME!" /quiet InstallAllUsers=0 PrependPath=1 TargetDir="!INSTALL_DIR!" Include_test=0
        if !errorlevel! neq 0 (
            echo [ERROR] Python installation failed.
            pause
            exit /b 1
        )
        
        del "%TEMP%\!INSTALLER_NAME!" >nul 2>&1
        
        if not exist "!PYTHON_CMD!" (
            echo [ERROR] Python was installed but cannot be located at "!PYTHON_CMD!".
            pause
            exit /b 1
        )
        echo [INFO] Python installed successfully!
    ) else (
        echo [INFO] Found Python at "!PYTHON_CMD!"
    )
)

:: Create virtual environment if it doesn't exist
if not exist .venv (
    echo [INFO] Creating Python virtual environment in .venv...
    "!PYTHON_CMD!" -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
echo [INFO] Verifying and installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Run the app
echo [INFO] Launching app...
python main.py
if %errorlevel% neq 0 (
    echo [ERROR] Application exited with an error code.
    pause
)

exit /b 0
