@echo off
REM MAMA-AI Production Deployment Script for Windows
REM Run this script to prepare and deploy to production

echo.
echo 🚀 MAMA-AI Production Deployment Preparation
echo ==============================================

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found. Please run this script from the MAMA-AI directory.
    pause
    exit /b 1
)

echo 📋 Pre-deployment checklist:

REM Check for required files
echo Checking required files...
if exist "app.py" (echo   ✅ app.py) else (echo   ❌ app.py ^(missing^))
if exist "requirements.txt" (echo   ✅ requirements.txt) else (echo   ❌ requirements.txt ^(missing^))
if exist "Procfile" (echo   ✅ Procfile) else (echo   ❌ Procfile ^(missing^))
if exist ".env.production" (echo   ✅ .env.production) else (echo   ❌ .env.production ^(missing^))
if exist "runtime.txt" (echo   ✅ runtime.txt) else (echo   ❌ runtime.txt ^(missing^))

REM Check Python version
echo.
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo   ❌ Python not found or not in PATH
) else (
    echo   ✅ Python is available
)

echo.
echo ⚙️ Environment Configuration:
if exist ".env" (
    echo   📄 .env file exists
    findstr /C:"your_" .env >nul 2>&1
    if %errorlevel% equ 0 (
        echo   ⚠️ Warning: Found placeholder values in .env
        echo     Please update API keys before deployment
    )
    
    findstr /C:"FLASK_ENV=production" .env >nul 2>&1
    if %errorlevel% equ 0 (
        echo   ✅ Production environment configured
    ) else (
        echo   ⚠️ Consider setting FLASK_ENV=production
    )
) else (
    echo   ⚠️ .env file not found. Copy from .env.production
)

echo.
echo 🧪 Testing local application:
echo Starting quick health check...

REM Start app in background for testing
start /min python app.py
timeout /t 5 /nobreak >nul

REM Test health endpoint using PowerShell
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:5000/health' -TimeoutSec 5 | Out-Null; Write-Host '  ✅ Application starts successfully' } catch { Write-Host '  ❌ Application failed to start' -ForegroundColor Red }"

REM Run production tests if available
if exist "production_test.py" (
    echo   🔬 Running production tests...
    python production_test.py --quick --url http://localhost:5000
)

REM Cleanup - kill any running Python processes (be careful in production!)
taskkill /f /im python.exe >nul 2>&1

echo.
echo 📂 Git Status:
git status >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('git status --porcelain ^| find /c /v ""') do set uncommitted=%%i
    if !uncommitted! equ 0 (
        echo   ✅ All changes committed
    ) else (
        echo   ⚠️ !uncommitted! uncommitted changes
        echo     Run: git add . ^&^& git commit -m "Production ready"
    )
    
    for /f "delims=" %%i in ('git branch --show-current') do set current_branch=%%i
    echo   📍 Current branch: !current_branch!
) else (
    echo   ❌ Not a git repository
)

echo.
echo 🌐 Heroku Deployment Steps:
echo 1. Ensure you have Heroku CLI installed
echo 2. Login to Heroku: heroku login
echo 3. Create app: heroku create mama-ai-health-assistant
echo 4. Add PostgreSQL: heroku addons:create heroku-postgresql:mini
echo 5. Set environment variables:
echo    heroku config:set FLASK_ENV=production
echo    heroku config:set SECRET_KEY=your-secure-key
echo    heroku config:set AFRICASTALKING_USERNAME=your-username
echo    heroku config:set AFRICASTALKING_API_KEY=your-api-key
echo    heroku config:set OPENAI_API_KEY=your-openai-key
echo 6. Deploy: git push heroku main
echo 7. Check logs: heroku logs --tail

echo.
echo 🔒 Security Checklist:
echo   📋 Update all API keys to production values
echo   📋 Set strong SECRET_KEY ^(minimum 32 characters^)
echo   📋 Never commit real API keys to git
echo   📋 Use PostgreSQL for production database
echo   📋 Enable HTTPS in production

echo.
echo 📋 Post-Deployment Tasks:
echo   📋 Configure Africa's Talking webhooks
echo   📋 Test SMS functionality
echo   📋 Verify AI responses
echo   📋 Monitor application logs
echo   📋 Set up monitoring and alerts

echo.
echo ✨ Your MAMA-AI system is ready for production deployment!
echo Follow the steps above to deploy to Heroku.
echo.
echo For detailed instructions, see: PRODUCTION_DEPLOYMENT.md

echo.
echo 🚀 Quick Deploy Command:
echo After setting up Heroku app and environment variables:
echo git add . ^&^& git commit -m "Production deployment" ^&^& git push heroku main

echo.
pause
