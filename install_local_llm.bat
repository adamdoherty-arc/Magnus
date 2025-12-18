@echo off
REM ==================================================
REM Magnus Local LLM Installation Script
REM Installs Ollama and downloads optimized models
REM ==================================================

echo ========================================
echo    MAGNUS LOCAL LLM INSTALLER
echo    NVIDIA RTX 4090 Optimized
echo ========================================
echo.

REM Check if Ollama is already installed
where ollama >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Ollama is already installed
    ollama --version
    echo.
) else (
    echo [!] Ollama is not installed
    echo.
    echo Please install Ollama from: https://ollama.ai/download/windows
    echo.
    echo After installation, run this script again
    pause
    exit /b 1
)

echo ========================================
echo    DOWNLOADING MODELS
echo ========================================
echo.
echo This will download approximately 70GB of models
echo Estimated time: 30-60 minutes (depending on internet speed)
echo.
echo Models to be installed:
echo   1. Qwen 2.5 32B (Primary)    - ~20GB
echo   2. Qwen 2.5 14B (Fast)       - ~9GB
echo   3. Llama 3.3 70B (Complex)   - ~40GB
echo.

set /p CONFIRM="Continue with download? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Installation cancelled
    exit /b 0
)

echo.
echo ========================================
echo    STEP 1: Qwen 2.5 14B (Fast Model)
echo ========================================
echo.
ollama pull qwen2.5:14b-instruct-q4_K_M
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download Qwen 2.5 14B
    pause
    exit /b 1
)
echo [OK] Qwen 2.5 14B installed

echo.
echo ========================================
echo    STEP 2: Qwen 2.5 32B (Primary Model)
echo ========================================
echo.
ollama pull qwen2.5:32b-instruct-q4_K_M
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download Qwen 2.5 32B
    pause
    exit /b 1
)
echo [OK] Qwen 2.5 32B installed

echo.
echo ========================================
echo    STEP 3: Llama 3.3 70B (Complex Model)
echo ========================================
echo.
echo [INFO] This is a large model (~40GB)
set /p INSTALL_70B="Install Llama 3.3 70B? (y/n): "
if /i "%INSTALL_70B%"=="y" (
    ollama pull llama3.3:70b-instruct-q4_K_M
    if %errorlevel% neq 0 (
        echo [WARNING] Failed to download Llama 3.3 70B
        echo You can install it later with: ollama pull llama3.3:70b-instruct-q4_K_M
    ) else (
        echo [OK] Llama 3.3 70B installed
    )
) else (
    echo [SKIP] Llama 3.3 70B installation skipped
)

echo.
echo ========================================
echo    VERIFYING INSTALLATION
echo ========================================
echo.
ollama list

echo.
echo ========================================
echo    TESTING MODEL
echo ========================================
echo.
echo Testing Qwen 2.5 32B with a sample query...
echo.
ollama run qwen2.5:32b-instruct-q4_K_M "Explain what a cash-secured put is in one sentence." --verbose false

echo.
echo ========================================
echo    INSTALLATION COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Test the integration: python src/magnus_local_llm.py
echo 2. Start the dashboard: streamlit run dashboard.py
echo 3. The AVA agent will now use local models
echo.
echo Performance tips:
echo - Close other GPU-intensive applications
echo - Ensure latest NVIDIA drivers are installed
echo - Monitor GPU usage with: nvidia-smi
echo.
echo For troubleshooting, see: LOCAL_LLM_INTEGRATION_PLAN.md
echo.

pause
