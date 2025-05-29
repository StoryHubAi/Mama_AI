# PowerShell Script to Setup Voice Testing with ngrok
# Run this script to automatically setup your voice testing environment

Write-Host "🎙️ MAMA-AI Voice Testing Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Check if Flask app is running
Write-Host "`n1️⃣ Checking if Flask app is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Flask app is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Flask app is not running. Starting it now..." -ForegroundColor Red
    Write-Host "Starting Flask app in background..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; python app.py" -WindowStyle Minimized
    Write-Host "Waiting for app to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

# Check if ngrok exists
Write-Host "`n2️⃣ Checking for ngrok..." -ForegroundColor Yellow
if (Test-Path ".\ngrok.exe") {
    Write-Host "✅ ngrok found!" -ForegroundColor Green
} else {
    Write-Host "❌ ngrok not found. Please download it from https://ngrok.com/download" -ForegroundColor Red
    Write-Host "Extract ngrok.exe to this folder: $PWD" -ForegroundColor Yellow
    
    # Try to download ngrok automatically
    Write-Host "`nAttempting to download ngrok..." -ForegroundColor Yellow
    try {
        if (Test-Path ".\ngrok.zip") {
            Write-Host "Found ngrok.zip, extracting..." -ForegroundColor Yellow
            Expand-Archive -Path ".\ngrok.zip" -DestinationPath "." -Force
            Write-Host "✅ ngrok extracted!" -ForegroundColor Green
        } else {
            Write-Host "Please download ngrok manually and run this script again." -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit
        }
    } catch {
        Write-Host "Please download ngrok manually from https://ngrok.com/download" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit
    }
}

# Start ngrok
Write-Host "`n3️⃣ Starting ngrok..." -ForegroundColor Yellow
Write-Host "This will create a public URL for your local app..." -ForegroundColor Gray

# Start ngrok in background and capture output
$ngrokProcess = Start-Process -FilePath ".\ngrok.exe" -ArgumentList "http", "5000" -PassThru -WindowStyle Minimized

# Wait for ngrok to start
Start-Sleep -Seconds 3

# Get ngrok URL
Write-Host "`n4️⃣ Getting ngrok URL..." -ForegroundColor Yellow
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method GET
    $publicUrl = $ngrokApi.tunnels[0].public_url
    
    if ($publicUrl -like "https://*") {
        Write-Host "✅ ngrok is running!" -ForegroundColor Green
        Write-Host "Public URL: $publicUrl" -ForegroundColor Cyan
        
        # Update .env file
        Write-Host "`n5️⃣ Updating .env file..." -ForegroundColor Yellow
        if (Test-Path ".env") {
            $envContent = Get-Content ".env"
            $envContent = $envContent -replace "BASE_URL=.*", "BASE_URL=$publicUrl"
            $envContent | Set-Content ".env"
            Write-Host "✅ .env file updated with ngrok URL!" -ForegroundColor Green
        } else {
            Write-Host "❌ .env file not found. Please copy .env.example to .env first." -ForegroundColor Red
        }
        
        Write-Host "`n🎉 Setup Complete!" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Gray
        Write-Host "Your voice callback URL is: $publicUrl/voice" -ForegroundColor Cyan
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "1. Go to your Africa's Talking dashboard" -ForegroundColor White
        Write-Host "2. Navigate to Voice > Voice Numbers" -ForegroundColor White
        Write-Host "3. Set callback URL to: $publicUrl/voice" -ForegroundColor Cyan
        Write-Host "4. Test by calling your voice number!" -ForegroundColor White
        Write-Host "`nPress Enter to run voice tests..." -ForegroundColor Yellow
        Read-Host
        
        # Run voice tests
        Write-Host "`n6️⃣ Running voice tests..." -ForegroundColor Yellow
        python test_voice.py
        
    } else {
        Write-Host "❌ Could not get ngrok URL" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Could not connect to ngrok API" -ForegroundColor Red
    Write-Host "Please check if ngrok started correctly" -ForegroundColor Yellow
}

Write-Host "`n📞 Ready for voice testing!" -ForegroundColor Green
Write-Host "You can now call your Africa's Talking voice number to test." -ForegroundColor White
Write-Host "`nTo stop ngrok, close the ngrok window or press Ctrl+C" -ForegroundColor Gray
Read-Host "`nPress Enter to exit"
