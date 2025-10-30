"""Client for interacting with the BrainyTots backend API."""
import httpx
import logging
import json
from typing import Optional, Dict, Any, List
from .config import settings
from .models import (
    BackendSessionStartRequest,
    BackendSessionStartResponse,
    BackendAssistantQueryRequest,
    BackendAssistantMessage,
    BackendSessionCloseRequest,
    BackendSessionCloseResponse
)

logger = logging.getLogger(__name__)


class BackendClient:
    """Client for communicating with the BrainyTots backend API."""

    def __init__(self):
        self.base_url = settings.backend_api_url.rstrip("/")

    async def start_session(
        self,
        child_name: str,
        dob: str,
        gestational_weeks: Optional[int] = None,
        locale: str = "en"
    ) -> BackendSessionStartResponse:
        """
        Start a new assessment session in the backend.

        Args:
            child_name: Child's name
            dob: Date of birth in ISO format (YYYY-MM-DD)
            gestational_weeks: Gestational weeks if premature
            locale: Language code (en, hi, mr)

        Returns:
            Session start response with session_id and age info
        """
        url = f"{self.base_url}/session/start"
        payload = BackendSessionStartRequest(
            child_name=child_name,
            dob=dob,
            gestational_weeks=gestational_weeks,
            locale=locale
        ).dict()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Started session {data['session_id']} for {child_name}")
                return BackendSessionStartResponse(**data)
        except Exception as e:
            logger.error(f"Failed to start session for {child_name}: {e}")
            raise

    async def query_assistant(
        self,
        session_id: str,
        user_message: str,
        answer_code: Optional[str] = None,
        confidence_override: Optional[str] = "sure"
    ) -> BackendAssistantMessage:
        """
        Send a message to the backend assistant and get the response.

        NOTE: The backend uses SSE (Server-Sent Events) streaming, but for WhatsApp
        we need synchronous responses. This method accumulates the complete response.

        Args:
            session_id: Session UUID
            user_message: User's message text
            answer_code: Answer code (yes/sometimes/no/not_sure)
            confidence_override: Confidence level (sure/somewhat/not_sure)

        Returns:
            Complete assistant message
        """
        url = f"{self.base_url}/assistant/query"
        payload = BackendAssistantQueryRequest(
            session_id=session_id,
            user_message=user_message,
            answer_code=answer_code,
            confidence_override=confidence_override
        ).dict(exclude_none=True)

        try:
            # Use streaming to handle SSE response
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()

                    # Accumulate SSE events
                    complete_content = ""
                    is_final = False
                    metadata = None

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue

                        # Parse SSE data
                        try:
                            data_str = line[6:]  # Remove "data: " prefix
                            if data_str == "[DONE]":
                                break

                            data = json.loads(data_str)
                            content_chunk = data.get("content", "")
                            complete_content += content_chunk

                            if data.get("is_final"):
                                is_final = True
                                metadata = data.get("metadata")
                        except json.JSONDecodeError:
                            continue

                    assistant_message = BackendAssistantMessage(
                        content=complete_content.strip(),
                        role="assistant",
                        is_final=is_final,
                        metadata=metadata
                    )

                    logger.info(f"Received response for session {session_id}, is_final={is_final}")
                    return assistant_message

        except Exception as e:
            logger.error(f"Failed to query assistant for session {session_id}: {e}")
            raise

    async def close_session(self, session_id: str) -> BackendSessionCloseResponse:
        """
        Close an assessment session and trigger scoring.

        Args:
            session_id: Session UUID

        Returns:
            Session close response with stats
        """
        url = f"{self.base_url}/session/close"
        payload = BackendSessionCloseRequest(session_id=session_id).dict()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Closed session {session_id}")
                return BackendSessionCloseResponse(**data)
        except Exception as e:
            logger.error(f"Failed to close session {session_id}: {e}")
            raise

    async def get_results(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive results for a completed session.

        Args:
            session_id: Session UUID

        Returns:
            Complete results including domain scores and recommendations
        """
        url = f"{self.base_url}/results"
        params = {"session_id": session_id}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Retrieved results for session {session_id}")
                return data
        except Exception as e:
            logger.error(f"Failed to get results for session {session_id}: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the backend API is healthy.

        Returns:
            True if healthy, False otherwise
        """
        url = f"{self.base_url}/healthz"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Backend health check failed: {e}")
            return False


# Global client instance
backend_client = BackendClient()
