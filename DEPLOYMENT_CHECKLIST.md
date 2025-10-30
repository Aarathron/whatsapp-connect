# Deployment Checklist

Use this checklist to deploy the WhatsApp Connect service to production.

## Pre-Deployment

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `WHAPI_API_TOKEN` with your actual token
- [ ] Set `WHAPI_CHANNEL_ID` with your channel ID
- [ ] Set `WHATSAPP_NUMBER` with your WhatsApp Business number
- [ ] Set `BACKEND_API_URL` to your backend API (e.g., http://localhost:8000)
- [ ] Set `DATABASE_URL` to your PostgreSQL database
- [ ] Set `LOG_LEVEL` to INFO for production
- [ ] Verify all environment variables are correct

### 2. Dependencies
- [ ] Python 3.10+ installed
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] No installation errors

### 3. Backend Connectivity
- [ ] Backend API is running
- [ ] Can access backend health: `curl http://localhost:8000/healthz`
- [ ] Backend database is accessible
- [ ] Backend has necessary milestones seeded

### 4. Whapi Configuration
- [ ] Whapi.cloud account active
- [ ] WhatsApp Business account connected
- [ ] Channel created and verified
- [ ] API token generated
- [ ] Test API token works: `curl -H "Authorization: Bearer YOUR_TOKEN" https://gate.whapi.cloud/health`

## Local Testing

### 5. Service Startup
- [ ] Service starts without errors: `python -m uvicorn src.main:app --reload --port 8001`
- [ ] Health endpoint works: `curl http://localhost:8001/health`
- [ ] Backend connectivity confirmed in startup logs
- [ ] No critical errors in logs

### 6. Webhook Testing (Local)
- [ ] ngrok installed: `ngrok http 8001`
- [ ] ngrok URL obtained (e.g., https://abc123.ngrok.io)
- [ ] Whapi webhook configured to ngrok URL
- [ ] Test message sent to WhatsApp number
- [ ] Webhook received (check logs)
- [ ] Bot responded with welcome message

### 7. Flow Testing
- [ ] Language selection works
- [ ] Name input works
- [ ] DOB parsing works (test various formats)
- [ ] Gestational question works
- [ ] Assessment starts successfully
- [ ] Questions display with buttons
- [ ] Buttons work correctly
- [ ] Assessment completes
- [ ] Results link received
- [ ] Results link opens correctly

### 8. Edge Cases
- [ ] Invalid date format handled
- [ ] Invalid gestational weeks handled
- [ ] Help command works
- [ ] Restart command works
- [ ] Multiple users can use simultaneously
- [ ] Errors don't crash service

## Production Deployment

### 9. Server Setup
- [ ] Production server accessible (e.g., 94.136.188.253)
- [ ] Python 3.10+ installed on server
- [ ] Code deployed to server
- [ ] Virtual environment created on server
- [ ] Dependencies installed on server

### 10. Service Configuration
- [ ] `.env` file created on server with production values
- [ ] Firewall allows port 8001 (or configured port)
- [ ] SSL/TLS certificate configured (if using HTTPS directly)
- [ ] Reverse proxy configured (nginx/apache) if needed

### 11. Process Management
Choose one:

#### Option A: Systemd Service
- [ ] Service file created: `/etc/systemd/system/whatsapp-connect.service`
- [ ] Service enabled: `sudo systemctl enable whatsapp-connect`
- [ ] Service started: `sudo systemctl start whatsapp-connect`
- [ ] Service status OK: `sudo systemctl status whatsapp-connect`
- [ ] Logs accessible: `journalctl -u whatsapp-connect -f`

#### Option B: Docker
- [ ] Dockerfile created
- [ ] Image built: `docker build -t whatsapp-connect .`
- [ ] Container started: `docker run -d -p 8001:8001 --env-file .env whatsapp-connect`
- [ ] Container running: `docker ps`

#### Option C: PM2
- [ ] PM2 installed: `npm install -g pm2`
- [ ] Service started: `pm2 start ecosystem.config.js`
- [ ] Service saved: `pm2 save`
- [ ] Startup configured: `pm2 startup`

### 12. Whapi Production Webhook
- [ ] Production URL is public (e.g., https://brainytots.com/whatsapp/webhook)
- [ ] Whapi webhook updated to production URL
- [ ] Webhook URL accessible: `curl https://your-domain.com/webhook`
- [ ] Webhook receives test events

### 13. Monitoring Setup
- [ ] Log file location configured
- [ ] Log rotation configured
- [ ] Health check endpoint monitored
- [ ] Alert system configured for failures
- [ ] Uptime monitoring enabled (e.g., UptimeRobot)

### 14. Production Testing
- [ ] Send test message to production number
- [ ] Complete full assessment flow
- [ ] Verify results link works
- [ ] Test from different devices
- [ ] Test all 3 languages
- [ ] Test error scenarios

## Post-Deployment

### 15. Documentation
- [ ] Production URL documented
- [ ] Access credentials documented
- [ ] Restart procedures documented
- [ ] Troubleshooting guide updated
- [ ] Team members trained

### 16. Monitoring
- [ ] Check logs daily for first week
- [ ] Monitor error rates
- [ ] Monitor response times
- [ ] Monitor completion rates
- [ ] Track user feedback

### 17. Backup & Recovery
- [ ] Database backup configured (when DB is added)
- [ ] Recovery procedure tested
- [ ] Rollback plan documented

## Future Enhancements

### 18. Database Integration (HIGH PRIORITY)
- [ ] Create database models
- [ ] Create Alembic migrations
- [ ] Run migrations
- [ ] Update state management methods
- [ ] Test state persistence
- [ ] Test resume functionality

### 19. Reminders (Celery)
- [ ] Redis installed and running
- [ ] Celery worker configured
- [ ] Reminder task implemented
- [ ] Celery beat configured
- [ ] Test reminders work

### 20. Analytics
- [ ] Analytics tracking added
- [ ] Dashboard created
- [ ] Reports configured

## Sign-Off

### Pre-Production
- [ ] All pre-deployment checks passed
- [ ] All local testing passed
- [ ] Code reviewed
- [ ] Security reviewed

### Production
- [ ] All production deployment steps completed
- [ ] All production tests passed
- [ ] Monitoring configured
- [ ] Documentation updated

### Final Approval
- [ ] Product owner approval
- [ ] Technical lead approval
- [ ] Operations team notified

---

## Quick Reference Commands

### Start Service
```bash
# Development
python -m uvicorn src.main:app --reload --port 8001

# Production (systemd)
sudo systemctl start whatsapp-connect

# Production (docker)
docker start whatsapp-connect

# Production (pm2)
pm2 start whatsapp-connect
```

### Check Status
```bash
# Health check
curl http://localhost:8001/health

# Systemd status
sudo systemctl status whatsapp-connect

# Docker status
docker ps | grep whatsapp-connect

# PM2 status
pm2 status whatsapp-connect
```

### View Logs
```bash
# Direct run (in terminal)
# Logs appear in terminal

# Systemd
journalctl -u whatsapp-connect -f

# Docker
docker logs -f whatsapp-connect

# PM2
pm2 logs whatsapp-connect
```

### Restart Service
```bash
# Systemd
sudo systemctl restart whatsapp-connect

# Docker
docker restart whatsapp-connect

# PM2
pm2 restart whatsapp-connect
```

---

**Deployment Date**: _________________

**Deployed By**: _________________

**Sign-off**: _________________
