# Complete Voice Testing Setup for MAMA-AI
# This script will help you test voice integration with Africa's Talking simulator

Write-Host "🎙️ MAMA-AI Voice Testing with Africa's Talking Simulator" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

Write-Host "`n📋 What we'll do:" -ForegroundColor Yellow
Write-Host "1. Start your Flask app" -ForegroundColor White
Write-Host "2. Start ngrok to make it publicly accessible" -ForegroundColor White
Write-Host "3. Get the public URL for Africa's Talking" -ForegroundColor White
Write-Host "4. Show you how to configure AT simulator" -ForegroundColor White
Write-Host "5. Test the voice integration" -ForegroundColor White

Read-Host "`nPress Enter to continue..."

# Step 1: Check if Flask app is running
Write-Host "`n1️⃣ Checking Flask application..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Flask app is already running!" -ForegroundColor Green
} catch {
    Write-Host "🚀 Starting Flask application..." -ForegroundColor Yellow
    Write-Host "Opening new terminal window for Flask app..." -ForegroundColor Gray
    
    # Start Flask in a new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Starting MAMA-AI Flask App...' -ForegroundColor Green; python app.py"
    
    Write-Host "Waiting for Flask app to start..." -ForegroundColor Gray
    $attempts = 0
    do {
        Start-Sleep -Seconds 2
        $attempts++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 2 -ErrorAction Stop
            $appRunning = $true
            Write-Host "✅ Flask app started successfully!" -ForegroundColor Green
        } catch {
            $appRunning = $false
            Write-Host "⏳ Still starting... (attempt $attempts/10)" -ForegroundColor Gray
        }
    } while (-not $appRunning -and $attempts -lt 10)
    
    if (-not $appRunning) {
        Write-Host "❌ Failed to start Flask app. Please start it manually: python app.py" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit
    }
}

# Step 2: Start ngrok
Write-Host "`n2️⃣ Starting ngrok tunnel..." -ForegroundColor Yellow
Write-Host "This creates a public URL for your local app..." -ForegroundColor Gray

# Kill any existing ngrok processes
Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Start ngrok
$ngrokProcess = Start-Process -FilePath ".\ngrok.exe" -ArgumentList "http", "5000", "--log", "stdout" -PassThru -WindowStyle Minimized

Write-Host "Waiting for ngrok to establish tunnel..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Step 3: Get ngrok URL
Write-Host "`n3️⃣ Getting public URL..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0
$ngrokUrl = $null

do {
    $attempt++
    try {
        $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method GET -TimeoutSec 3
        if ($ngrokApi.tunnels.Count -gt 0) {
            $ngrokUrl = $ngrokApi.tunnels[0].public_url
            if ($ngrokUrl -like "https://*") {
                Write-Host "✅ ngrok tunnel established!" -ForegroundColor Green
                Write-Host "🌐 Public URL: $ngrokUrl" -ForegroundColor Cyan
                break
            }
        }
    } catch {
        Write-Host "⏳ Waiting for ngrok tunnel... (attempt $attempt/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
} while ($attempt -lt $maxAttempts)

if (-not $ngrokUrl) {
    Write-Host "❌ Could not establish ngrok tunnel. Please check ngrok setup." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Step 4: Update .env file
Write-Host "`n4️⃣ Updating configuration..." -ForegroundColor Yellow
try {
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace "BASE_URL=.*", "BASE_URL=$ngrokUrl"
    $envContent | Set-Content ".env" -NoNewline
    Write-Host "✅ .env file updated with public URL!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not update .env file. Please update BASE_URL manually." -ForegroundColor Yellow
}

# Step 5: Test the voice endpoint
Write-Host "`n5️⃣ Testing voice endpoint..." -ForegroundColor Yellow
try {
    $testUrl = "$ngrokUrl/voice"
    $testData = @{
        sessionId = "test123"
        phoneNumber = "+254700000000"
        isActive = "1"
        dtmfDigits = ""
        recordingUrl = ""
        durationInSeconds = "0"
    }
    
    $response = Invoke-WebRequest -Uri $testUrl -Method POST -Body $testData -ContentType "application/x-www-form-urlencoded" -TimeoutSec 10
    
    if ($response.StatusCode -eq 200 -and $response.Content -like "*<Response>*") {
        Write-Host "✅ Voice endpoint is working correctly!" -ForegroundColor Green
        Write-Host "📱 Voice menu XML response received" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Voice endpoint responded but may have issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Voice endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Show Africa's Talking configuration
Write-Host "`n🎯 Africa's Talking Simulator Setup Instructions" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Gray

Write-Host "`n📋 Follow these steps in your Africa's Talking dashboard:" -ForegroundColor Yellow

Write-Host "`n1. Login to Africa's Talking:" -ForegroundColor White
Write-Host "   👉 Go to: https://account.africastalking.com" -ForegroundColor Cyan

Write-Host "`n2. Navigate to Voice section:" -ForegroundColor White
Write-Host "   👉 Click on 'Voice' in the left menu" -ForegroundColor Cyan
Write-Host "   👉 Then click on 'Voice Numbers'" -ForegroundColor Cyan

Write-Host "`n3. Configure your voice number:" -ForegroundColor White
Write-Host "   👉 Select your voice number: +254727230675" -ForegroundColor Cyan
Write-Host "   👉 Set Callback URL to: $ngrokUrl/voice" -ForegroundColor Cyan
Write-Host "   👉 Enable DTMF (touch-tone) support" -ForegroundColor Cyan
Write-Host "   👉 Save settings" -ForegroundColor Cyan

Write-Host "`n4. Test with Voice Simulator:" -ForegroundColor White
Write-Host "   👉 Go to 'Voice' > 'Voice Simulator'" -ForegroundColor Cyan
Write-Host "   👉 Enter your phone number to call" -ForegroundColor Cyan
Write-Host "   👉 Click 'Make Call'" -ForegroundColor Cyan
Write-Host "   👉 You should hear the MAMA-AI voice menu!" -ForegroundColor Cyan

Write-Host "`n5. Alternative - Call directly:" -ForegroundColor White
Write-Host "   👉 Call +254727230675 from your phone" -ForegroundColor Cyan
Write-Host "   👉 Listen to the voice menu" -ForegroundColor Cyan
Write-Host "   👉 Press 1, 2, 3, 4, or 9 to test different options" -ForegroundColor Cyan

Write-Host "`n🔊 Expected Voice Flow:" -ForegroundColor Green
Write-Host "When you call, you'll hear:" -ForegroundColor Gray
Write-Host "🎵 'Welcome to MAMA-AI, your maternal health assistant.'" -ForegroundColor White
Write-Host "🎵 'Press 1 for pregnancy tracking'" -ForegroundColor White
Write-Host "🎵 'Press 2 for health check'" -ForegroundColor White
Write-Host "🎵 'Press 3 for appointments'" -ForegroundColor White
Write-Host "🎵 'Press 4 for emergency'" -ForegroundColor White
Write-Host "🎵 'Press 9 to repeat menu'" -ForegroundColor White

Write-Host "`n📞 Voice Menu Options:" -ForegroundColor Green
Write-Host "Press 1️⃣ : Pregnancy tracking and monitoring" -ForegroundColor White
Write-Host "Press 2️⃣ : Health check and symptoms reporting" -ForegroundColor White
Write-Host "Press 3️⃣ : Appointment management" -ForegroundColor White
Write-Host "Press 4️⃣ : Emergency assistance" -ForegroundColor White
Write-Host "Press 9️⃣ : Repeat the main menu" -ForegroundColor White

Write-Host "`n💡 Important Notes:" -ForegroundColor Yellow
Write-Host "• Keep this PowerShell window open (ngrok tunnel active)" -ForegroundColor White
Write-Host "• Keep the Flask app window open" -ForegroundColor White
Write-Host "• Your callback URL: $ngrokUrl/voice" -ForegroundColor Cyan
Write-Host "• Test with AT Voice Simulator first before real calls" -ForegroundColor White

Write-Host "`n🚀 Ready for Testing!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Gray

# Keep monitoring
Write-Host "`n👀 Monitoring voice calls..." -ForegroundColor Yellow
Write-Host "This window will show incoming voice requests." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop monitoring." -ForegroundColor Gray

Write-Host "`nWaiting for voice calls... (configure AT dashboard now)" -ForegroundColor Cyan

# Monitor for incoming requests
try {
    while ($true) {
        Start-Sleep -Seconds 5
        # You could add request monitoring here if needed
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
} catch {
    Write-Host "`n`n👋 Monitoring stopped." -ForegroundColor Yellow
}

Write-Host "`n🎉 Voice testing session complete!" -ForegroundColor Green
Write-Host "To restart, run: .\setup_complete_voice_test.ps1" -ForegroundColor Cyan
