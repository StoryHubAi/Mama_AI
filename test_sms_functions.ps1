# MAMA-AI SMS Testing Functions for PowerShell
# Usage: . .\test_sms_functions.ps1  (to load functions)

function Send-TestSMS {
    param(
        [string]$PhoneNumber = "+254700000000",
        [string]$Message = "Hello from MAMA-AI!"
    )
    
    $body = @{
        phone_number = $PhoneNumber
        message = $Message
    } | ConvertTo-Json
      try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/test-sms" -Method POST -Headers @{"Content-Type"="application/json"} -Body $body
        Write-Host "✅ SMS Sent Successfully!" -ForegroundColor Green
        Write-Host "📱 To: $PhoneNumber" -ForegroundColor Cyan
        Write-Host "💬 Message: $Message" -ForegroundColor Cyan
        Write-Host "📊 Response: $($response.Content)" -ForegroundColor Yellow
    }
    catch {
        Write-Host "❌ Error sending SMS: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-IncomingSMS {
    param(
        [string]$FromNumber = "+254700000001",
        [string]$Message = "I need help with pregnancy advice",
        [string]$ToShortcode = "985"
    )
    
    $body = "from=$([System.Web.HttpUtility]::UrlEncode($FromNumber))&to=$ToShortcode&text=$([System.Web.HttpUtility]::UrlEncode($Message))&date=2025-05-27 18:50:00"
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/sms" -Method POST -Headers @{"Content-Type"="application/x-www-form-urlencoded"} -Body $body
        Write-Host "📩 Incoming SMS Processed!" -ForegroundColor Green
        Write-Host "📞 From: $FromNumber" -ForegroundColor Cyan
        Write-Host "💬 Message: $Message" -ForegroundColor Cyan
        Write-Host "🤖 AI Response: $($response.Content)" -ForegroundColor Yellow
    }
    catch {
        Write-Host "❌ Error processing incoming SMS: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-EmergencyScenarios {
    Write-Host "🚨 Testing Emergency Detection..." -ForegroundColor Red
    
    $emergencies = @(
        @{Phone="+254700000001"; Message="EMERGENCY: I have severe bleeding and cramping"},
        @{Phone="+254700000002"; Message="I can't feel my baby moving for 6 hours"},
        @{Phone="+254700000003"; Message="I have terrible headache and blurred vision"},
        @{Phone="+254700000004"; Message="Having contractions every 3 minutes at 35 weeks"}
    )
    
    foreach ($emergency in $emergencies) {
        Write-Host "`n--- Testing Emergency Scenario ---" -ForegroundColor Yellow
        Test-IncomingSMS -FromNumber $emergency.Phone -Message $emergency.Message
        Start-Sleep -Seconds 1
    }
}

function Test-RegularQueries {
    Write-Host "💊 Testing Regular Health Queries..." -ForegroundColor Blue
    
    $queries = @(
        @{Phone="+254700000005"; Message="What foods should I avoid during pregnancy?"},
        @{Phone="+254700000006"; Message="How often should I feel baby movements?"},
        @{Phone="+254700000007"; Message="Ninahisi kichefuchefu asubuhi. Nifanye nini?"},
        @{Phone="+254700000008"; Message="When is my next appointment?"}
    )
    
    foreach ($query in $queries) {
        Write-Host "`n--- Testing Regular Query ---" -ForegroundColor Yellow
        Test-IncomingSMS -FromNumber $query.Phone -Message $query.Message
        Start-Sleep -Seconds 1
    }
}

function Test-AllSMSScenarios {
    Write-Host "🔄 Running Complete SMS Test Suite..." -ForegroundColor Magenta
    
    # Test SMS Sending
    Write-Host "`n📤 Testing SMS Sending..." -ForegroundColor Green
    Send-TestSMS -PhoneNumber "+254700000010" -Message "Welcome to MAMA-AI! Your AI health assistant is ready to help."
    
    Start-Sleep -Seconds 2
    
    # Test Regular Queries
    Test-RegularQueries
    
    Start-Sleep -Seconds 2
    
    # Test Emergency Scenarios
    Test-EmergencyScenarios
    
    Write-Host "`n✅ All SMS tests completed!" -ForegroundColor Green
}

# Load System.Web for URL encoding
Add-Type -AssemblyName System.Web

Write-Host "🤱 MAMA-AI SMS Testing Functions Loaded!" -ForegroundColor Green
Write-Host "Available Commands:" -ForegroundColor Cyan
Write-Host "  Send-TestSMS -PhoneNumber '+254700000000' -Message 'Your message'" -ForegroundColor White
Write-Host "  Test-IncomingSMS -FromNumber '+254700000001' -Message 'Your message'" -ForegroundColor White
Write-Host "  Test-EmergencyScenarios" -ForegroundColor White
Write-Host "  Test-RegularQueries" -ForegroundColor White
Write-Host "  Test-AllSMSScenarios" -ForegroundColor White
