@echo off
SETLOCAL EnableDelayedExpansion

echo.
echo ===========================================================================
echo                   MAGNUS LOCAL LLM - QUICK SETUP
echo                   Run this AFTER installing Ollama
echo ===========================================================================
echo.

REM Verify Ollama is installed
echo Checking Ollama installation...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Ollama is not installed or not in PATH!
    echo.
    echo Please install Ollama first:
    echo 1. Go to: C:\Users\New User\Downloads\
    echo 2. Double-click: OllamaSetup.exe
    echo 3. Complete installation
    echo 4. Re-run this script
    echo.
    pause
    exit /b 1
)

echo [OK] Ollama is installed!
ollama --version
echo.

REM Check GPU
echo Checking NVIDIA GPU...
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Could not detect GPU, but continuing...
)
echo.

REM Download Primary Model (Qwen 32B)
echo ===========================================================================
echo Downloading PRIMARY MODEL: Qwen 2.5 32B (~20GB)
echo This will take 10-20 minutes depending on your internet speed
echo ===========================================================================
echo.

ollama list | findstr "qwen2.5:32b" >nul 2>&1
if %errorlevel%==0 (
    echo [SKIP] Qwen 2.5 32B already installed
) else (
    echo [DOWNLOADING] Please wait...
    ollama pull qwen2.5:32b-instruct-q4_K_M
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to download. Trying alternative tag...
        ollama pull qwen2.5:32b-instruct
    )
    echo [OK] Primary model downloaded!
)
echo.

REM Download Fast Model (Qwen 14B)
echo ===========================================================================
echo Downloading FAST MODEL: Qwen 2.5 14B (~9GB)
echo This will take 5-10 minutes
echo ===========================================================================
echo.

ollama list | findstr "qwen2.5:14b" >nul 2>&1
if %errorlevel%==0 (
    echo [SKIP] Qwen 2.5 14B already installed
) else (
    echo [DOWNLOADING] Please wait...
    ollama pull qwen2.5:14b-instruct-q4_K_M
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to download. Trying alternative tag...
        ollama pull qwen2.5:14b-instruct
    )
    echo [OK] Fast model downloaded!
)
echo.

REM Optional 70B model
echo ===========================================================================
echo OPTIONAL: Llama 3.3 70B (~40GB, 30-60 min download)
echo ===========================================================================
set /p INSTALL_70B="Download Llama 3.3 70B for complex analysis? (y/n): "
if /i "!INSTALL_70B!"=="y" (
    ollama list | findstr "llama3.3:70b" >nul 2>&1
    if !errorlevel!==0 (
        echo [SKIP] Llama 3.3 70B already installed
    ) else (
        echo [DOWNLOADING] This will take a while...
        ollama pull llama3.3:70b-instruct-q4_K_M
        if !errorlevel! neq 0 (
            ollama pull llama3.3:70b-instruct
        )
    )
) else (
    echo [SKIP] Skipping 70B model
)
echo.

REM Test with Python
echo ===========================================================================
echo Testing Python Integration
echo ===========================================================================
echo.
cd /d "C:\code\Magnus"
python test_local_llm.py
if %errorlevel% neq 0 (
    echo [WARNING] Some tests failed, but models should work
)
echo.

REM Summary
echo ===========================================================================
echo                    SETUP COMPLETE!
echo ===========================================================================
echo.
echo Installed models:
ollama list
echo.
echo Your RTX 4090 is ready for local AI!
echo.
echo Next steps:
echo 1. Start Magnus dashboard: streamlit run dashboard.py
echo 2. Or use in Python: from src.magnus_local_llm import get_magnus_llm
echo.
echo Documentation: LOCAL_LLM_QUICKSTART.md
echo.
pause
ENDLOCAL
