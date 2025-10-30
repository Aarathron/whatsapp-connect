"""Webhook handler for processing incoming Whapi messages."""
import logging
from typing import List
from .models import WhapiWebhookPayload, WhapiMessage
from .conversation_flow import ConversationFlowHandler

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Processes incoming Whapi webhook events."""

    def __init__(self, flow_handler: ConversationFlowHandler):
        self.flow_handler = flow_handler

    async def process_webhook(self, payload: List[WhapiWebhookPayload]):
        """
        Process incoming Whapi webhook payload.

        Args:
            payload: List of webhook payloads (Whapi sends as array)
        """
        for item in payload:
            # Check event type
            if item.event.type != "messages" or item.event.event != "post":
                logger.debug(f"Skipping non-message event: {item.event.type}/{item.event.event}")
                continue

            # Process each message
            for message in item.messages:
                await self.process_message(message)

    async def process_message(self, message: WhapiMessage):
        """
        Process a single incoming message.

        Args:
            message: Whapi message object
        """
        # Ignore messages sent by us
        if message.from_me:
            logger.debug(f"Skipping own message: {message.id}")
            return

        # Extract phone number and name
        phone = message.from_
        user_name = message.from_name

        # Extract message content
        message_text = None
        is_button_response = False

        if message.type == "text" and message.text:
            message_text = message.text.body
        elif message.type == "button" and message.button_response:
            message_text = message.button_response.text
            is_button_response = True
        else:
            logger.warning(f"Unsupported message type: {message.type}")
            return

        if not message_text:
            logger.warning(f"No message text found in message {message.id}")
            return

        logger.info(f"Processing message from {phone} ({user_name}): {message_text[:50]}")

        try:
            # Handle the message through conversation flow
            await self.flow_handler.handle_message(
                phone=phone,
                user_name=user_name,
                message_text=message_text,
                is_button_response=is_button_response
            )
        except Exception as e:
            logger.error(f"Error processing message from {phone}: {e}", exc_info=True)
            # Don't raise - we want to return 200 OK to Whapi anyway
