# 🔧 VS Code Port Forwarding Troubleshooting Guide

## Current Issue: 502 Bad Gateway

The VS Code tunnel `https://k99gkq4s-5000.euw.devtunnels.ms/` is returning a 502 error, which means:
- The tunnel is active 
- But it can't reach your Flask app on port 5000

## ✅ Step-by-Step Fix:

### 1. Check Flask App Status
Make sure your Flask app is running properly:

```powershell
# Check if Flask is running on port 5000
netstat -an | findstr ":5000"
```

You should see something like:
```
TCP    0.0.0.0:5000          0.0.0.0:0              LISTENING
```

### 2. Check VS Code Port Forwarding

In VS Code:
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type: `Port Forward` 
3. Look for "Ports: Focus on Ports View"
4. Check if port 5000 is listed and status is "Active"

### 3. Restart Flask App with Correct Binding

Your Flask app might be binding to localhost only. Let's fix this:

```python
# In app.py, make sure you have:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 4. Test Local Connection First

Before testing the tunnel, verify Flask works locally:

```powershell
# Test local Flask app
Invoke-RestMethod -Uri "http://127.0.0.1:5000/sms" -Method POST -Body @{from="+254712345678"; to="15629"; text="test"; date="2025-05-29"}
```

### 5. Alternative: Use Different Port

If port 5000 is having issues:

1. Change Flask to port 8000:
   ```python
   app.run(host='0.0.0.0', port=8000, debug=True)
   ```

2. Update VS Code port forwarding to port 8000

3. New tunnel URL would be like: `https://k99gkq4s-8000.euw.devtunnels.ms/`

## 🧪 Quick Test Commands

### Test 1: Check if Flask is running
```powershell
curl http://127.0.0.1:5000/
```

### Test 2: Test SMS endpoint locally  
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/sms" -Method POST -Body @{from="+254712345678"; to="15629"; text="test local"; date="2025-05-29"}
```

### Test 3: Test tunnel connection
```powershell
curl https://k99gkq4s-5000.euw.devtunnels.ms/
```

## 🎯 Expected Results

✅ **Local test should return**: Flask app response or error message  
✅ **Tunnel test should return**: Same response as local test  
✅ **SMS test should return**: `{"status": "success", "message": "SMS processed"}`

## 📱 Once Fixed: Africa's Talking Setup

When the tunnel is working:

1. **SMS Callback URL**: `https://k99gkq4s-5000.euw.devtunnels.ms/sms`
2. **Delivery Report URL**: `https://k99gkq4s-5000.euw.devtunnels.ms/delivery-report`

Set these in your Africa's Talking dashboard under SMS settings.

## 🔄 Alternative Testing Method

If tunnel continues having issues, you can test directly with Africa's Talking simulator by:

1. Running Flask locally
2. Using a service like ngrok
3. Or testing the SMS logic with our test scripts

**Your SMS AI service code is perfect - we just need to get the tunnel working! 🚀**
