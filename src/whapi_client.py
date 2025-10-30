"""Client for interacting with Whapi.cloud API."""
import httpx
import logging
from typing import List, Optional
from .config import settings
from .models import WhapiButton

logger = logging.getLogger(__name__)


class WhapiClient:
    """Client for sending messages via Whapi.cloud API."""

    def __init__(self):
        self.base_url = settings.whapi_api_url.rstrip('/')
        self.token = settings.whapi_api_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def send_text(self, phone: str, body: str) -> dict:
        """
        Send a text message to a WhatsApp number.

        Args:
            phone: Phone number (e.g., "919665507774")
            body: Message text

        Returns:
            Response from Whapi API
        """
        url = f"{self.base_url}/messages/text"
        payload = {
            "to": phone,
            "body": body
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Sent text message to {phone}")
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send text message to {phone}: {e}")
            raise

    async def send_buttons(self, phone: str, body: str, buttons: List[str]) -> dict:
        """
        Send a message with interactive buttons.

        Args:
            phone: Phone number
            body: Message text
            buttons: List of button titles (max 3)

        Returns:
            Response from Whapi API
        """
        url = f"{self.base_url}/messages/interactive"

        # Whapi expects buttons in this format
        button_objects = [
            {"type": "reply", "reply": {"id": f"btn_{i}", "title": title}}
            for i, title in enumerate(buttons[:3])  # Whapi max 3 buttons per message
        ]

        payload = {
            "to": phone,
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": button_objects
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Sent button message to {phone} with {len(buttons)} buttons")
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send button message to {phone}: {e}")
            raise

    async def send_link(self, phone: str, body: str, url: str) -> dict:
        """
        Send a message with a link preview.

        Args:
            phone: Phone number
            body: Message text (should include the URL)
            url: The URL to preview

        Returns:
            Response from Whapi API
        """
        # For Whapi, we just send text with URL and it auto-generates preview
        return await self.send_text(phone, body)

    async def send_list(self, phone: str, body: str, button_text: str, sections: List[dict]) -> dict:
        """
        Send a message with a list of options.

        Args:
            phone: Phone number
            body: Message text
            button_text: Text for the button that opens the list
            sections: List sections with rows

        Returns:
            Response from Whapi API
        """
        url = f"{self.base_url}/messages/interactive"

        payload = {
            "to": phone,
            "type": "list",
            "body": {"text": body},
            "action": {
                "button": button_text,
                "sections": sections
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Sent list message to {phone}")
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send list message to {phone}: {e}")
            raise

    async def mark_as_read(self, message_id: str) -> dict:
        """Mark a message as read."""
        url = f"{self.base_url}/messages/{message_id}/read"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"Failed to mark message {message_id} as read: {e}")
            return {}


# Global client instance
whapi_client = WhapiClient()
