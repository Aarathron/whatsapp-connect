# BrainyTots WhatsApp Connect

WhatsApp integration service that enables users to complete developmental assessments via WhatsApp and receive results as a web link.

## Features

- 🌍 **Multi-language Support**: English, Hindi, and Marathi
- 📱 **Interactive Conversations**: Button-based responses for easy interaction
- 🔄 **State Management**: Resume incomplete assessments
- 🎯 **Smart Routing**: Conversation state machine for guided assessment flow
- 📊 **Results Delivery**: Web link to detailed results on BrainyTots website
- 🔔 **Reminders**: Automated reminders for incomplete assessments (coming soon)

## Architecture

```
WhatsApp User → Whapi.cloud → WhatsApp Connect Service → Backend API
                                       ↓
                               State Management
                               Message Translation
                               Button Handling
```

## Project Structure

```
whatsapp-connect/
├── src/
│   ├── __init__.py               # Package init
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Settings and configuration
│   ├── models.py                 # Pydantic models
│   ├── webhook_handler.py        # Webhook processing
│   ├── conversation_flow.py      # State machine logic
│   ├── message_templates.py      # Multi-language templates
│   ├── whapi_client.py           # Whapi API client
│   └── backend_client.py         # Backend API client
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## Setup

### Prerequisites

- Python 3.10+
- Whapi.cloud account with API token
- BrainyTots backend API running
- PostgreSQL database (for state persistence)

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd /root/developmental\ area\ mapping/whatsapp-connect
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your actual values
   ```

   Required variables:
   - `WHAPI_API_TOKEN`: Your Whapi.cloud API token
   - `WHAPI_CHANNEL_ID`: Your Whapi channel ID
   - `WHATSAPP_NUMBER`: Your WhatsApp Business number
   - `BACKEND_API_URL`: URL of the BrainyTots backend (e.g., http://localhost:8000)
   - `DATABASE_URL`: PostgreSQL connection string

### Running the Service

#### Development Mode

```bash
# From whatsapp-connect directory
python -m uvicorn src.main:app --reload --port 8765
```

The service will start on `http://localhost:8765`

#### Production Mode

```bash
# Using uvicorn directly
uvicorn src.main:app --host 0.0.0.0 --port 8765 --workers 4

# Or with gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8765
```

### Deploying on Coolify

- Select the `Dockerfile` build type and ensure the `Port Exposes` field includes `8765`.
- Coolify injects a `PORT` environment variable at runtime matching the first exposed port, so the container must bind to `$PORT` ([Coolify docs](https://raw.githubusercontent.com/coollabsio/coolify-docs/v4.x/docs/knowledge-base/environment-variables.md)).
- Provide required secrets (Whapi token, backend URLs, etc.) via Coolify's Environment tab; optional runtime tuning such as `GUNICORN_WORKERS` and `GUNICORN_LOG_LEVEL` can be added there too.
- After deployment, set the Whapi webhook URL to `https://<your-domain>/webhook` so inbound messages reach the FastAPI service.
```

### Setting Up Whapi Webhook

1. **Expose your local server** (for development):
   ```bash
   ngrok http 8765
   ```

   Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

2. **Configure Whapi webhook**:
   - Go to Whapi.cloud dashboard
   - Navigate to your channel settings
   - Set webhook URL to: `https://your-domain.com/webhook` (or ngrok URL for testing)
   - Enable webhook for "messages" events

3. **Test the webhook**:
   - Send a message to your WhatsApp Business number
   - Check the service logs for incoming webhook events

## API Endpoints

### `GET /`
Health check endpoint.

**Response**:
```json
{
  "service": "BrainyTots WhatsApp Connect",
  "version": "1.0.0",
  "status": "running"
}
```

### `GET /health`
Detailed health status including backend connectivity.

**Response**:
```json
{
  "status": "healthy",
  "backend": "up"
}
```

### `POST /webhook`
Webhook endpoint for receiving messages from Whapi.cloud.

**Request**: Whapi webhook payload (see [Whapi documentation](https://whapi.readme.io))

**Response**:
```json
{
  "status": "ok"
}
```

### `GET /qr-code`
Generate WhatsApp link for users to start assessment.

**Response**:
```json
{
  "wa_link": "https://wa.me/YOUR_NUMBER?text=Start",
  "message": "Scan this QR code or click the link to start assessment",
  "instructions": "Use a QR code generator to create a QR code from wa_link"
}
```

## Conversation Flow

### 1. Welcome & Language Selection
```
User: (sends any message)
Bot: Welcome message with language buttons
     [English] [हिंदी] [मराठी]
```

### 2. Session Initialization
```
Bot: What's your child's name?
User: Aarav
Bot: When was Aarav born? (DD/MM/YYYY)
User: 15/03/2024
Bot: Was Aarav born prematurely?
     [Yes] [No]
```

### 3. Assessment Questions
```
Bot: Question 5 of ~12
     Can Aarav sit without support?
     [Yes] [Sometimes] [No] [Not Sure]
User: [Yes]
Bot: (Next question...)
```

### 4. Results Delivery
```
Bot: 🎉 Assessment complete for Aarav!

     📊 Quick summary:
     • Age: 8 months
     • Questions: 12
     • Overall: On track

     View detailed results:
     https://brainytots.com/pages/assessment-results?session_id=xxx
```

## Message Templates

All messages are available in 3 languages:
- **English** (en)
- **Hindi** (hi)
- **Marathi** (mr)

Templates are defined in `src/message_templates.py` and include:
- Welcome messages
- Session creation prompts
- Assessment question formats
- Results messages
- Error messages
- Help text

## Backend Integration

The service integrates with the BrainyTots backend API:

### Session Management
- `POST /session/start` - Create new assessment session
- `POST /session/close` - Finalize session and trigger scoring

### Assessment Flow
- `POST /assistant/query` - Send user answers and get next question
- `GET /results` - Retrieve comprehensive results

### SSE Handling
The backend uses Server-Sent Events (SSE) for streaming responses. The WhatsApp service accumulates the complete response before sending to the user.

## State Management

Conversation state is tracked per user (phone number) and includes:
- Current conversation step
- Collected data (name, DOB, etc.)
- Backend session ID
- Question count
- Last activity timestamp

**Note**: Database integration is pending. Current implementation uses in-memory state (will be lost on restart).

## Development

### Adding New Languages

1. Add translations to `src/message_templates.py`:
   ```python
   WELCOME_MESSAGES: Dict[str, str] = {
       "en": "Welcome...",
       "hi": "स्वागत...",
       "mr": "स्वागत...",
       "ta": "வரவேற்பு..."  # Add Tamil
   }
   ```

2. Add language button and code mapping:
   ```python
   LANGUAGE_BUTTONS = ["English", "हिंदी", "मराठी", "தமிழ்"]
   LANGUAGE_CODE_MAP = {
       ...
       "தமிழ்": "ta",
       "tamil": "ta"
   }
   ```

### Adding New Conversation States

1. Add state to enum in `src/models.py`:
   ```python
   class ConversationState(str, Enum):
       ...
       NEW_STATE = "new_state"
   ```

2. Add handler in `src/conversation_flow.py`:
   ```python
   async def handle_new_state(self, phone, message_text, state_data):
       # Implementation
       pass
   ```

3. Add routing in `handle_message()`:
   ```python
   elif state_data.current_step == ConversationState.NEW_STATE:
       await self.handle_new_state(phone, message_text, state_data)
   ```

## Testing

### Manual Testing Checklist

- [ ] User receives welcome message
- [ ] Language selection works
- [ ] Session creation collects all data
- [ ] Date validation works (DD/MM/YYYY)
- [ ] Gestational weeks validation (24-42)
- [ ] Assessment questions display with buttons
- [ ] Answer buttons work correctly
- [ ] Progress indicator shows
- [ ] Assessment completes successfully
- [ ] Results link is sent and opens correctly
- [ ] Resume functionality works
- [ ] Help command works
- [ ] Restart command works

### Logs

Monitor logs for debugging:
```bash
# Watch logs in real-time
tail -f logs/whatsapp-connect.log

# Or use journalctl if running as systemd service
journalctl -u whatsapp-connect -f
```

## Troubleshooting

### Webhook Not Receiving Messages

1. Check Whapi webhook configuration
2. Verify webhook URL is accessible (use ngrok for local testing)
3. Check service logs for incoming requests
4. Verify Whapi channel is active

### Backend Connection Issues

```bash
# Test backend connectivity
curl http://localhost:8000/healthz

# Check backend URL in .env
echo $BACKEND_API_URL
```

### State Not Persisting

Database integration is pending. State is currently in-memory and will be lost on restart.

**Solution**: Implement database models and persistence layer (see TODO comments in code).

## Deployment

### Systemd Service (Linux)

1. Create service file `/etc/systemd/system/whatsapp-connect.service`:
   ```ini
   [Unit]
   Description=BrainyTots WhatsApp Connect
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/developmental area mapping/whatsapp-connect
   Environment="PATH=/root/developmental area mapping/whatsapp-connect/venv/bin"
   ExecStart=/root/developmental area mapping/whatsapp-connect/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8765
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start:
   ```bash
   sudo systemctl enable whatsapp-connect
   sudo systemctl start whatsapp-connect
   sudo systemctl status whatsapp-connect
   ```

### Docker Deployment (Future)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8765"]
```

## Roadmap

- [x] Core conversation flow
- [x] Multi-language support
- [x] Backend API integration
- [x] Session creation and management
- [x] Assessment question handling
- [x] Results delivery
- [ ] Database persistence for state management
- [ ] Resume incomplete sessions
- [ ] Automated reminders (Celery tasks)
- [ ] Analytics and metrics
- [ ] User management dashboard
- [ ] Broadcast messaging capability

## Contributing

This is an internal BrainyTots project. For questions or issues, contact the development team.

## License

Proprietary - BrainyTots © 2025
