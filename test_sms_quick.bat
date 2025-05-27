@echo off
echo ========================================
echo MAMA-AI SMS Quick Test Commands
echo ========================================
echo.

echo 1. Testing SMS Sending...
echo.
curl -X POST http://localhost:5000/test-sms -H "Content-Type: application/json" -d "{\"phone_number\":\"+254700000001\",\"message\":\"Hello from MAMA-AI! How are you feeling today?\"}"
echo.
echo.

echo 2. Testing Regular Health Query...
echo.
curl -X POST http://localhost:5000/sms -H "Content-Type: application/x-www-form-urlencoded" -d "from=+254700000001&to=985&text=What foods should I avoid during pregnancy?&date=2025-05-27 18:45:00"
echo.
echo.

echo 3. Testing Emergency Detection...
echo.
curl -X POST http://localhost:5000/sms -H "Content-Type: application/x-www-form-urlencoded" -d "from=+254700000002&to=985&text=EMERGENCY: I have severe bleeding and pain&date=2025-05-27 18:46:00"
echo.
echo.

echo 4. Testing Kiswahili Message...
echo.
curl -X POST http://localhost:5000/sms -H "Content-Type: application/x-www-form-urlencoded" -d "from=+254700000003&to=985&text=Ninahisi kichefuchefu asubuhi. Nifanye nini?&date=2025-05-27 18:47:00"
echo.
echo.

echo ========================================
echo SMS Testing Complete!
echo ========================================
pause
