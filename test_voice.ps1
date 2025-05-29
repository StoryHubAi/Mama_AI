# PowerShell script to test MAMA-AI Voice Integration
# Run this script to test voice functionality

Write-Host "🎙️ MAMA-AI Voice Integration Test" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if the app is running
Write-Host "`nChecking if Flask app is running..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Flask app is running!" -ForegroundColor Green
    } else {
        Write-Host "❌ Flask app health check failed!" -ForegroundColor Red
        Write-Host "Please start the app with: python app.py" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Cannot connect to Flask app on http://localhost:5000" -ForegroundColor Red
    Write-Host "Please start the app with: python app.py" -ForegroundColor Yellow
    exit 1
}

# Run the Python test script
Write-Host "`nRunning voice integration tests..." -ForegroundColor Yellow
python test_voice.py

Write-Host "`n🎉 Testing complete!" -ForegroundColor Green
Write-Host "`nTo configure Africa's Talking Voice:" -ForegroundColor Cyan
Write-Host "1. Login to your Africa's Talking dashboard" -ForegroundColor White
Write-Host "2. Go to Voice > Phone Numbers" -ForegroundColor White
Write-Host "3. Set callback URL to: https://yourdomain.com/voice" -ForegroundColor White
Write-Host "4. Update your .env file with your voice number" -ForegroundColor White
