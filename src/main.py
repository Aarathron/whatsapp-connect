"""Main FastAPI application for WhatsApp Connect service."""
import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import after logging is configured
from .config import settings
from .models import WhapiWebhookPayload
from .webhook_handler import WebhookHandler
from .conversation_flow import ConversationFlowHandler
from .backend_client import backend_client

# Create FastAPI app
app = FastAPI(
    title="BrainyTots WhatsApp Connect",
    description="WhatsApp integration for developmental assessments",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting BrainyTots WhatsApp Connect service...")
    logger.info(f"Backend API URL: {settings.backend_api_url}")
    logger.info(f"Whapi Channel ID: {settings.whapi_channel_id}")

    # Check backend health
    is_healthy = await backend_client.health_check()
    if is_healthy:
        logger.info("Backend API is healthy [OK]")
    else:
        logger.warning("Backend API health check failed [WARNING]")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "BrainyTots WhatsApp Connect",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check backend connectivity
    backend_healthy = await backend_client.health_check()

    return {
        "status": "healthy" if backend_healthy else "degraded",
        "backend": "up" if backend_healthy else "down"
    }


@app.post("/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint for receiving messages from Whapi.cloud.

    This endpoint receives webhook events from Whapi and processes them
    in the background to ensure quick response time.
    """
    try:
        # Parse webhook payload
        payload_data = await request.json()
        logger.debug(f"Received webhook payload: {payload_data}")

        # Validate payload structure
        try:
            if isinstance(payload_data, dict):
                payload_data = [payload_data]
            elif not isinstance(payload_data, list):
                raise ValueError(f"Unsupported payload type: {type(payload_data)}")
            payload = [WhapiWebhookPayload(**item) for item in payload_data]
        except Exception as e:
            logger.error(f"Invalid webhook payload structure: {e}")
            # Still return 200 to prevent Whapi retries
            return {"status": "error", "message": "Invalid payload structure"}

        # Process webhook in background
        background_tasks.add_task(process_webhook_background, payload)

        # Return immediately to Whapi
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error in webhook endpoint: {e}", exc_info=True)
        # Return 200 anyway to prevent retries
        return {"status": "error", "message": str(e)}


async def process_webhook_background(payload: List[WhapiWebhookPayload]):
    """
    Process webhook in background task.

    Args:
        payload: List of webhook payloads
    """
    try:
        # Create conversation flow handler
        # TODO: Pass actual database session once DB is set up
        flow_handler = ConversationFlowHandler(db=None)

        # Create webhook handler
        webhook_handler = WebhookHandler(flow_handler)

        # Process the webhook
        await webhook_handler.process_webhook(payload)

    except Exception as e:
        logger.error(f"Error processing webhook in background: {e}", exc_info=True)


@app.get("/qr-code")
async def generate_qr_code():
    """
    Generate QR code for WhatsApp link.

    Returns a wa.me link that users can scan or click to start conversation.
    """
    # WhatsApp link with pre-filled message
    wa_link = f"https://wa.me/{settings.whatsapp_number}?text=Start"

    return {
        "wa_link": wa_link,
        "message": "Scan this QR code or click the link to start assessment",
        "instructions": "Use a QR code generator to create a QR code from wa_link"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
