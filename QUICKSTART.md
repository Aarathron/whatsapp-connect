# Quick Start Guide

Get your WhatsApp assessment bot running in 5 minutes!

## Prerequisites

- Whapi.cloud account with API token ✓ (you have this)
- BrainyTots backend running on http://localhost:8000
- Python 3.10+

## Step 1: Install Dependencies

```bash
cd "/root/developmental area mapping/whatsapp-connect"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Configure Environment

Create `.env` file:

```bash
cat > .env << 'EOF'
# Whapi Configuration (REPLACE WITH YOUR ACTUAL VALUES)
WHAPI_API_TOKEN=your_actual_whapi_token_here
WHAPI_API_URL=https://gate.whapi.cloud
WHAPI_CHANNEL_ID=FALCON-SW9M2
WHATSAPP_NUMBER=your_whatsapp_number

# Backend API Configuration
BACKEND_API_URL=http://localhost:8000

# Database Configuration
DATABASE_URL=postgresql://postgres:password@94.136.188.253:5432/bt-devtracker

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Session Configuration
SESSION_TIMEOUT_HOURS=24
REMINDER_DELAY_HOURS=2
MAX_RESUME_HOURS=48

# Server Configuration
HOST=0.0.0.0
PORT=8765
LOG_LEVEL=INFO
EOF
```

**IMPORTANT**: Replace the following values with your actual credentials:
- `WHAPI_API_TOKEN` - Your Whapi.cloud API token
- `WHATSAPP_NUMBER` - Your WhatsApp Business number
- `WHAPI_CHANNEL_ID` - Your Whapi channel ID (if different)

## Step 3: Start the Service

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Start the service
python -m uvicorn src.main:app --reload --port 8765
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting BrainyTots WhatsApp Connect service...
INFO:     Backend API URL: http://localhost:8000
INFO:     Backend API is healthy ✓
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8765
```

## Step 4: Expose Your Service (For Testing)

### Option A: Using ngrok (Easiest for local testing)

```bash
# In a new terminal
ngrok http 8765
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Option B: Direct deployment (Production)

If you're on your server (94.136.188.253), configure your web server (nginx/apache) to proxy to port 8765.

## Step 5: Configure Whapi Webhook

1. Go to https://panel.whapi.cloud
2. Select your channel (FALCON-SW9M2)
3. Go to Settings → Webhooks
4. Set webhook URL to: `https://your-ngrok-url.ngrok.io/webhook` (or your production URL)
5. Enable "Messages" events
6. Save

## Step 6: Test It!

Send a message to your WhatsApp Business number:

```
Hi
```

You should receive:
```
👶 Welcome to BrainyTots Developmental Assessment!

I'll help you track your child's development with a quick 5-minute assessment.

Please select your preferred language:
[English] [हिंदी] [मराठी]
```

**If you see this, congratulations! Your bot is working! 🎉**

## Testing the Complete Flow

1. **Select Language**: Tap "English"
2. **Enter Name**: Type your child's name (e.g., "Aarav")
3. **Enter DOB**: Type date like "15/03/2024"
4. **Premature Question**: Tap "No" (or "Yes" and enter weeks if premature)
5. **Answer Questions**: Tap answer buttons for ~12 questions
6. **Get Results**: Receive link to results page

## Troubleshooting

### Service won't start
```bash
# Check if port 8765 is available
lsof -i :8765

# Check backend is running
curl http://localhost:8000/healthz
```

### No messages received
```bash
# Check service logs
# (They'll appear in the terminal where uvicorn is running)

# Verify webhook is configured correctly in Whapi dashboard

# Test webhook manually
curl -X POST http://localhost:8765/webhook \
  -H "Content-Type: application/json" \
  -d '[{"messages":[{"id":"test","from_me":false,"type":"text","chat_id":"test@s.whatsapp.net","timestamp":1234567890,"from":"1234567890","from_name":"Test User","text":{"body":"hello"}}],"event":{"type":"messages","event":"post"},"channel_id":"test"}]'
```

### Backend connection failed
```bash
# Check backend is accessible
curl http://localhost:8000/healthz

# If backend is on different machine, make sure firewall allows connection
```

## Next Steps

Once your bot is working:

1. **Add Database Persistence**: Implement database models for state management (see TODO comments)
2. **Add Reminders**: Implement Celery tasks for incomplete assessment reminders
3. **Deploy to Production**: Set up systemd service (see README.md)
4. **Monitor Usage**: Add analytics tracking
5. **Add QR Code to Website**: Integrate the `/qr-code` endpoint into your frontend

## Getting the WhatsApp Link

To get the link/QR code for users:

```bash
curl http://localhost:8765/qr-code
```

Response:
```json
{
  "wa_link": "https://wa.me/YOUR_NUMBER?text=Start",
  "message": "Scan this QR code or click the link to start assessment"
}
```

Use this link on your website or generate a QR code from it.

## Common Commands

```bash
# Start service
python -m uvicorn src.main:app --reload --port 8765

# Start with more workers (production)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8765

# Check health
curl http://localhost:8765/health

# View logs (if using systemd)
journalctl -u whatsapp-connect -f
```

## Support

For issues or questions, check:
1. Service logs in terminal
2. Whapi dashboard for webhook status
3. Backend API health: `curl http://localhost:8000/healthz`
4. README.md for detailed documentation

---

**Happy Testing! 🚀**
