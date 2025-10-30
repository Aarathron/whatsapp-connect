# WhatsApp Connect - Deployment Guide

Complete guide for deploying WhatsApp Connect to Coolify using Docker.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment Steps](#detailed-deployment-steps)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)
- [Monitoring](#monitoring)

---

## Prerequisites

### Required Services
- **Coolify Server** - Running and accessible
- **PostgreSQL Database** - External database configured
- **Redis Instance** - External Redis server (for future use)
- **Whapi.cloud Account** - Active with API token
- **GitHub Account** - For repository hosting

### Required Information
- Whapi API Token
- Whapi Channel ID
- WhatsApp Business Number
- Backend API URL
- PostgreSQL connection string
- Redis URL

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-username/whatsapp-connect.git
cd whatsapp-connect
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your actual values
nano .env
```

### 3. Build Docker Image
```bash
docker build -t whatsapp-connect:latest .
```

### 4. Run with Docker Compose
```bash
docker-compose up -d
```

### 5. Verify Deployment
```bash
# Check container status
docker ps

# Check logs
docker logs whatsapp-connect

# Test health endpoint
curl http://localhost:8001/health
```

---

## Detailed Deployment Steps

### Step 1: Prepare Your Coolify Server

1. **Access Coolify Dashboard**
   - Navigate to your Coolify instance
   - Log in to the admin panel

2. **Create New Project** (if needed)
   - Click "New Project"
   - Name: "WhatsApp Connect" or similar
   - Click "Create"

### Step 2: Set Up GitHub Repository

1. **Push Code to GitHub** (if not already done)
   ```bash
   cd /root/developmental\ area\ mapping/whatsapp-connect
   git init
   git add .
   git commit -m "Initial commit: WhatsApp Connect with Docker support"
   git branch -M main
   git remote add origin https://github.com/your-username/whatsapp-connect.git
   git push -u origin main
   ```

### Step 3: Configure Application in Coolify

1. **Add New Resource**
   - In your Coolify project, click "New Resource"
   - Select "Public Repository"

2. **Repository Configuration**
   - Repository URL: `https://github.com/your-username/whatsapp-connect.git`
   - Branch: `main`
   - Build Pack: `Dockerfile`
   - Dockerfile Location: `./Dockerfile`

3. **Port Configuration**
   - Application Port: `8001`
   - Exposed Port: `8001` (or your preferred external port)
   - Protocol: `HTTP`

4. **Domain Configuration** (optional)
   - Add your custom domain (e.g., `whatsapp.yourdomain.com`)
   - Or use Coolify-generated domain
   - Enable SSL/TLS if using custom domain

### Step 4: Configure Environment Variables

In Coolify's environment variables section, add:

```env
# Whapi Configuration
WHAPI_API_TOKEN=your_actual_token_here
WHAPI_API_URL=https://gate.whapi.cloud/
WHAPI_CHANNEL_ID=your_channel_id
WHATSAPP_NUMBER=your_whatsapp_number

# Backend API
BACKEND_API_URL=https://bt-development.skillit.in

# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Redis
REDIS_URL=redis://your-redis-host:6379/0

# Application Settings
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO
SESSION_TIMEOUT_HOURS=24
REMINDER_DELAY_HOURS=2
MAX_RESUME_HOURS=48
```

### Step 5: Configure Webhooks in Whapi.cloud

1. **Get Your Deployment URL**
   - After deployment, get your app's public URL from Coolify
   - Example: `https://whatsapp.yourdomain.com` or `https://abc123.coolify.io`

2. **Set Webhook in Whapi Dashboard**
   - Go to https://whapi.cloud/
   - Navigate to your channel settings
   - Set Webhook URL: `https://your-domain.com/webhook`
   - Enable webhook for: Messages, Status updates

3. **Test Webhook**
   ```bash
   curl -X POST https://your-domain.com/webhook \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

### Step 6: Deploy

1. **Trigger Deployment in Coolify**
   - Click "Deploy" button in Coolify
   - Monitor build logs for errors
   - Wait for deployment to complete

2. **Verify Deployment**
   ```bash
   # Check health endpoint
   curl https://your-domain.com/health
   
   # Expected response:
   # {
   #   "status": "healthy",
   #   "service": "WhatsApp Connect",
   #   "backend_status": "connected"
   # }
   ```

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `WHAPI_API_TOKEN` | Whapi.cloud API authentication token | `4F48RAbdWNvWM4Hc2s4A1WS5Wfu3Grz3` |
| `WHAPI_CHANNEL_ID` | Whapi channel identifier | `FALCON-SW9M2` |
| `WHATSAPP_NUMBER` | WhatsApp Business number | `918856946303` |
| `BACKEND_API_URL` | BrainyTots backend API URL | `https://bt-development.skillit.in` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WHAPI_API_URL` | `https://gate.whapi.cloud` | Whapi API base URL |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `SESSION_TIMEOUT_HOURS` | `24` | Session timeout duration |
| `REMINDER_DELAY_HOURS` | `2` | Delay before sending reminders |
| `MAX_RESUME_HOURS` | `48` | Maximum time to resume session |
| `HOST` | `0.0.0.0` | Server host binding |
| `PORT` | `8001` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker logs whatsapp-connect
```

**Common issues:**
- Missing required environment variables
- Database connection failure
- Port already in use

**Solutions:**
```bash
# Verify all required env vars are set
docker exec whatsapp-connect env | grep WHAPI

# Check port availability
sudo lsof -i :8001

# Test database connection
docker exec whatsapp-connect python -c "from src.config import settings; print(settings.DATABASE_URL)"
```

### Webhook Not Receiving Messages

**Check:**
1. Webhook URL is correctly configured in Whapi.cloud
2. Application is publicly accessible
3. Firewall allows incoming connections on port 8001
4. SSL certificate is valid (if using HTTPS)

**Test webhook manually:**
```bash
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "from": "918856946303",
      "body": "test",
      "type": "text"
    }]
  }'
```

### Backend Connection Errors

**Check:**
```bash
# Test backend connectivity from container
docker exec whatsapp-connect curl https://bt-development.skillit.in/healthz

# Check backend URL in environment
docker exec whatsapp-connect env | grep BACKEND_API_URL
```

### Health Check Failing

**Diagnose:**
```bash
# Check health endpoint
curl http://localhost:8001/health

# Check detailed health
curl http://localhost:8001/health -v

# Check application logs
docker logs -f whatsapp-connect
```

---

## Monitoring

### Health Checks

The application provides a health check endpoint:

```bash
curl https://your-domain.com/health
```

**Healthy Response:**
```json
{
  "status": "healthy",
  "service": "WhatsApp Connect",
  "backend_status": "connected",
  "version": "1.0.0"
}
```

**Unhealthy Response:**
```json
{
  "status": "unhealthy",
  "service": "WhatsApp Connect",
  "backend_status": "disconnected",
  "error": "Backend API unreachable"
}
```

### Logging

**View real-time logs:**
```bash
docker logs -f whatsapp-connect
```

**View specific log lines:**
```bash
docker logs whatsapp-connect --tail 100
```

**Search logs for errors:**
```bash
docker logs whatsapp-connect 2>&1 | grep ERROR
```

### Metrics to Monitor

1. **Container Status**
   ```bash
   docker ps | grep whatsapp-connect
   ```

2. **Memory Usage**
   ```bash
   docker stats whatsapp-connect
   ```

3. **Health Check**
   - Set up automated health checks in Coolify
   - Configure alerts for health check failures

4. **Application Metrics**
   - Monitor webhook response times
   - Track message processing success rate
   - Monitor backend API connectivity

---

## Updating the Application

### Method 1: Git Push (Auto-Deploy)

If Coolify is configured for auto-deploy:

```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```

Coolify will automatically rebuild and redeploy.

### Method 2: Manual Deploy

In Coolify dashboard:
1. Navigate to your application
2. Click "Redeploy"
3. Monitor build logs

### Method 3: Docker Image Update

```bash
# Build new image
docker build -t whatsapp-connect:latest .

# Stop current container
docker-compose down

# Start with new image
docker-compose up -d
```

---

## Scaling Considerations

### Current Limitations

- **In-Memory State**: Session state is stored in-memory (lost on restart)
- **Single Instance**: Not horizontally scalable without database implementation

### Future Improvements Needed

1. **Implement Database Persistence**
   - Store session state in PostgreSQL
   - Enable multi-instance deployment

2. **Add Redis Session Storage**
   - Use Redis for session management
   - Enable horizontal scaling

3. **Load Balancing**
   - Use Coolify's built-in load balancing
   - Configure multiple replicas

---

## Security Checklist

- [ ] Environment variables stored securely in Coolify (not in code)
- [ ] Database uses strong password
- [ ] SSL/TLS enabled for public endpoint
- [ ] Whapi API token kept secret
- [ ] Container runs as non-root user (configured in Dockerfile)
- [ ] Regular security updates applied
- [ ] Logs don't expose sensitive data

---

## Support

### Documentation
- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Detailed checklist

### External Resources
- [Coolify Documentation](https://coolify.io/docs)
- [Whapi.cloud API Docs](https://whapi.cloud/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated**: 2025-10-30
