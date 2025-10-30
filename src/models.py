"""Pydantic models for Whapi webhook payloads and application data."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ========== Whapi Webhook Models ==========

class WhapiTextMessage(BaseModel):
    """Text content from Whapi message."""
    body: str


class WhapiButtonResponse(BaseModel):
    """Button response from Whapi message."""
    text: str


class WhapiMessage(BaseModel):
    """Individual message from Whapi webhook."""
    id: str
    from_me: bool
    type: str  # "text", "button", "interactive", etc.
    chat_id: str  # "919665507774@s.whatsapp.net"
    timestamp: int
    from_: str = Field(alias="from")  # "919665507774"
    from_name: Optional[str] = None
    source: Optional[str] = None
    device_id: Optional[int] = None
    chat_name: Optional[str] = None

    # Message content fields (only one will be present based on type)
    text: Optional[WhapiTextMessage] = None
    button_response: Optional[WhapiButtonResponse] = None


class WhapiEvent(BaseModel):
    """Event metadata from Whapi webhook."""
    type: str  # "messages"
    event: str  # "post"


class WhapiWebhookPayload(BaseModel):
    """Complete webhook payload from Whapi."""
    messages: Optional[List[WhapiMessage]] = None
    statuses: Optional[List[Dict[str, Any]]] = None
    event: WhapiEvent
    channel_id: str


# ========== Conversation State Models ==========

class ConversationState(str, Enum):
    """Possible states in the conversation flow."""
    NEW = "new"
    LANGUAGE_SELECT = "language_select"
    ASK_NAME = "ask_name"
    ASK_DOB = "ask_dob"
    ASK_GESTATIONAL = "ask_gestational"
    ASK_GESTATIONAL_WEEKS = "ask_gestational_weeks"
    ASSESSMENT = "assessment"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class CollectedData(BaseModel):
    """Data collected during session initialization."""
    locale: Optional[str] = None
    child_name: Optional[str] = None
    dob: Optional[str] = None  # ISO format: YYYY-MM-DD
    is_premature: Optional[bool] = None
    gestational_weeks: Optional[int] = None


class ConversationStateData(BaseModel):
    """Complete conversation state stored in database."""
    current_step: ConversationState
    collected_data: CollectedData = CollectedData()
    session_id: Optional[str] = None  # Backend session UUID
    questions_asked: int = 0
    last_message_at: datetime
    last_question_id: Optional[str] = None


# ========== Whapi API Request Models ==========

class WhapiSendTextRequest(BaseModel):
    """Request to send text message via Whapi."""
    to: str  # Phone number
    body: str


class WhapiButton(BaseModel):
    """Button for interactive message."""
    title: str


class WhapiSendButtonsRequest(BaseModel):
    """Request to send message with buttons via Whapi."""
    to: str
    body: str
    buttons: List[WhapiButton]


class WhapiSendLinkRequest(BaseModel):
    """Request to send link preview message via Whapi."""
    to: str
    body: str
    # Whapi will automatically generate preview


# ========== Backend API Models ==========

class BackendSessionStartRequest(BaseModel):
    """Request to start a session in the backend."""
    child_name: str
    dob: str  # ISO format
    gestational_weeks: Optional[int] = None
    locale: str = "en"


class BackendSessionStartResponse(BaseModel):
    """Response from backend session start."""
    session_id: str
    child_name: str
    chronological_age_months: float
    corrected_age_months: Optional[float]
    using_corrected_age: bool
    age_band: str
    locale: str


class BackendAssistantQueryRequest(BaseModel):
    """Request to send message to backend assistant."""
    session_id: str
    user_message: str
    answer_code: Optional[str] = None
    confidence_override: Optional[str] = "sure"


class BackendAssistantMessage(BaseModel):
    """Message from backend assistant."""
    content: str
    role: str = "assistant"
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None


class BackendSessionCloseRequest(BaseModel):
    """Request to close a session."""
    session_id: str


class BackendSessionCloseResponse(BaseModel):
    """Response from backend session close."""
    message: str
    total_questions: int
    total_time_seconds: float
    domains_assessed: List[str]
