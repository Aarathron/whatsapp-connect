"""Conversation flow state machine for WhatsApp assessment bot."""
import logging
import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from .models import (
    ConversationState,
    ConversationStateData,
    CollectedData
)
from . import message_templates as templates
from .whapi_client import whapi_client
from .backend_client import backend_client
from .state_store import state_store

logger = logging.getLogger(__name__)


class ConversationFlowHandler:
    """Handles conversation state transitions and message routing."""

    def __init__(self, db: Session):
        self.db = db

    async def handle_message(
        self,
        phone: str,
        user_name: str,
        message_text: str,
        is_button_response: bool = False
    ):
        """
        Main entry point for handling incoming messages.

        Args:
            phone: User's phone number
            user_name: User's WhatsApp name
            message_text: The message content
            is_button_response: Whether this is a button click
        """
        # Check for special commands
        message_lower = message_text.lower().strip()
        if message_lower in ["restart", "start over", "new"]:
            await self.restart_conversation(phone)
            return
        elif message_lower in ["help", "info"]:
            await self.send_help(phone)
            return

        # Get or create conversation state
        state_data = await self.get_or_create_state(phone, user_name)

        # Route to appropriate handler based on current state
        if state_data.current_step == ConversationState.NEW:
            await self.handle_new_user(phone, state_data)
        elif state_data.current_step == ConversationState.LANGUAGE_SELECT:
            await self.handle_language_selection(phone, message_text, state_data)
        elif state_data.current_step == ConversationState.ASK_NAME:
            await self.handle_name_input(phone, message_text, state_data)
        elif state_data.current_step == ConversationState.ASK_DOB:
            await self.handle_dob_input(phone, message_text, state_data)
        elif state_data.current_step == ConversationState.ASK_GESTATIONAL:
            await self.handle_gestational_question(phone, message_text, state_data)
        elif state_data.current_step == ConversationState.ASK_GESTATIONAL_WEEKS:
            await self.handle_gestational_weeks(phone, message_text, state_data)
        elif state_data.current_step == ConversationState.ASSESSMENT:
            await self.handle_assessment_answer(phone, message_text, state_data)
        elif state_data.current_step == ConversationState.COMPLETED:
            await self.handle_completed_session(phone, state_data)

    async def handle_new_user(self, phone: str, state_data: ConversationStateData):
        """Welcome new user and ask for language preference."""
        # Send welcome message with language buttons
        welcome_msg = templates.WELCOME_MESSAGES["en"]
        await whapi_client.send_buttons(
            phone,
            welcome_msg,
            templates.LANGUAGE_BUTTONS
        )

        # Update state
        state_data.current_step = ConversationState.LANGUAGE_SELECT
        await self.save_state(phone, state_data)

    async def handle_language_selection(
        self,
        phone: str,
        message_text: str,
        state_data: ConversationStateData
    ):
        """Handle language selection."""
        message_lower = message_text.lower().strip()

        # Map button text to locale code
        locale = templates.LANGUAGE_CODE_MAP.get(message_lower)
        if not locale:
            # Try matching partial text
            for key, value in templates.LANGUAGE_CODE_MAP.items():
                if key in message_lower:
                    locale = value
                    break

        if not locale:
            # Default to English if unclear
            locale = "en"

        # Save locale
        state_data.collected_data.locale = locale

        # Ask for child's name
        ask_name_msg = templates.get_message(templates.ASK_NAME, locale)
        await whapi_client.send_text(phone, ask_name_msg)

        # Update state
        state_data.current_step = ConversationState.ASK_NAME
        await self.save_state(phone, state_data)

    async def handle_name_input(
        self,
        phone: str,
        message_text: str,
        state_data: ConversationStateData
    ):
        """Handle child's name input."""
        child_name = message_text.strip()

        # Save name
        state_data.collected_data.child_name = child_name

        # Ask for date of birth
        locale = state_data.collected_data.locale or "en"
        ask_dob_msg = templates.get_message(
            templates.ASK_DOB,
            locale,
            name=child_name
        )
        await whapi_client.send_text(phone, ask_dob_msg)

        # Update state
        state_data.current_step = ConversationState.ASK_DOB
        await self.save_state(phone, state_data)

    async def handle_dob_input(
        self,
        phone: str,
        message_text: str,
        state_data: ConversationStateData
    ):
        """Handle date of birth input."""
        locale = state_data.collected_data.locale or "en"
        child_name = state_data.collected_data.child_name

        # Try to parse date (supports DD/MM/YYYY, DD-MM-YYYY, etc.)
        dob_iso = self.parse_date(message_text)

        if not dob_iso:
            # Invalid format
            invalid_msg = templates.get_message(templates.INVALID_DOB, locale)
            await whapi_client.send_text(phone, invalid_msg)
            return

        # Save DOB
        state_data.collected_data.dob = dob_iso

        # Ask if premature
        ask_gestational_msg = templates.get_message(
            templates.ASK_GESTATIONAL,
            locale,
            name=child_name
        )
        await whapi_client.send_buttons(
            phone,
            ask_gestational_msg,
            templates.YES_NO_BUTTONS
        )

        # Update state
        state_data.current_step = ConversationState.ASK_GESTATIONAL
        await self.save_state(phone, state_data)

    async def handle_gestational_question(
        self,
        phone: str,
        message_text: str,
        state_data: ConversationStateData
    ):
        """Handle premature birth question."""
        locale = state_data.collected_data.locale or "en"
        child_name = state_data.collected_data.child_name
        message_lower = message_text.lower().strip()

        # Check response
        if message_lower in ["yes", "y", "9>", "9K/"]:
            # Ask for gestational weeks
            state_data.collected_data.is_premature = True
            ask_weeks_msg = templates.get_message(
                templates.ASK_GESTATIONAL_WEEKS,
                locale,
                name=child_name
            )
            await whapi_client.send_text(phone, ask_weeks_msg)

            state_data.current_step = ConversationState.ASK_GESTATIONAL_WEEKS
            await self.save_state(phone, state_data)
        else:
            # Not premature, start assessment
            state_data.collected_data.is_premature = False
            state_data.collected_data.gestational_weeks = None
            await self.start_assessment(phone, state_data)

    async def handle_gestational_weeks(
        self,
        phone: str,
        message_text: str,
        state_data: ConversationStateData
    ):
        """Handle gestational weeks input."""
        locale = state_data.collected_data.locale or "en"

        # Try to extract number
        try:
            weeks = int(re.findall(r'\d+', message_text)[0])
            if 24 <= weeks <= 42:
                state_data.collected_data.gestational_weeks = weeks
                await self.start_assessment(phone, state_data)
            else:
                # Invalid range
                invalid_msg = templates.get_message(
                    templates.INVALID_GESTATIONAL_WEEKS,
                    locale
                )
                await whapi_client.send_text(phone, invalid_msg)
        except (IndexError, ValueError):
            # Invalid format
            invalid_msg = templates.get_message(
                templates.INVALID_GESTATIONAL_WEEKS,
                locale
            )
            await whapi_client.send_text(phone, invalid_msg)

    async def start_assessment(self, phone: str, state_data: ConversationStateData):
        """Start the backend assessment session."""
        try:
            # Call backend to start session
            response = await backend_client.start_session(
                child_name=state_data.collected_data.child_name,
                dob=state_data.collected_data.dob,
                gestational_weeks=state_data.collected_data.gestational_weeks,
                locale=state_data.collected_data.locale or "en"
            )

            # Save session ID
            state_data.session_id = response.session_id

            # Send starting message
            locale = state_data.collected_data.locale or "en"
            starting_msg = templates.get_message(
                templates.STARTING_ASSESSMENT,
                locale,
                name=state_data.collected_data.child_name
            )
            await whapi_client.send_text(phone, starting_msg)

            # Get first question
            assistant_response = await backend_client.query_assistant(
                session_id=response.session_id,
                user_message="Start assessment",
                answer_code=None
            )

            # Send first question with buttons
            await self.send_question_with_buttons(
                phone,
                assistant_response.content,
                locale,
                state_data.questions_asked + 1
            )

            # Update state
            state_data.current_step = ConversationState.ASSESSMENT
            state_data.questions_asked += 1
            await self.save_state(phone, state_data)

        except Exception as e:
            logger.error(f"Failed to start assessment for {phone}: {e}")
            locale = state_data.collected_data.locale or "en"
            error_msg = templates.get_message(templates.ERROR_MESSAGES, locale)
            await whapi_client.send_text(phone, error_msg)

    async def handle_assessment_answer(
        self,
        phone: str,
        message_text: str,
        state_data: ConversationStateData
    ):
        """Handle answer to assessment question."""
        locale = state_data.collected_data.locale or "en"

        # Map answer text to answer code
        answer_text_lower = message_text.lower().strip()
        answer_code = templates.ANSWER_CODE_MAP.get(answer_text_lower)

        if not answer_code:
            # Try partial matching
            for key, value in templates.ANSWER_CODE_MAP.items():
                if key in answer_text_lower or answer_text_lower in key:
                    answer_code = value
                    break

        if not answer_code:
            # Invalid answer, re-send question
            last_question_msg = "Please select one of the options using the buttons."
            await whapi_client.send_text(phone, last_question_msg)
            return

        try:
            # Send answer to backend
            assistant_response = await backend_client.query_assistant(
                session_id=state_data.session_id,
                user_message=message_text,
                answer_code=answer_code,
                confidence_override="sure"
            )

            # Check if assessment is complete
            if assistant_response.is_final:
                await self.complete_assessment(phone, state_data)
            else:
                # Send next question
                await self.send_question_with_buttons(
                    phone,
                    assistant_response.content,
                    locale,
                    state_data.questions_asked + 1
                )

                state_data.questions_asked += 1
                await self.save_state(phone, state_data)

        except Exception as e:
            logger.error(f"Failed to process answer for {phone}: {e}")
            error_msg = templates.get_message(templates.ERROR_MESSAGES, locale)
            await whapi_client.send_text(phone, error_msg)

    async def complete_assessment(self, phone: str, state_data: ConversationStateData):
        """Complete the assessment and send results."""
        try:
            # Close session in backend
            close_response = await backend_client.close_session(state_data.session_id)

            # Get results summary
            results = await backend_client.get_results(state_data.session_id)

            # Build results URL
            results_url = f"https://brainytots.com/pages/assessment-results?session_id={state_data.session_id}"

            # Send completion message
            locale = state_data.collected_data.locale or "en"
            corrected_note = ""
            if results.get("using_corrected_age"):
                corrected_note = templates.get_message(
                    templates.CORRECTED_AGE_NOTE,
                    locale
                )

            completion_msg = templates.get_message(
                templates.ASSESSMENT_COMPLETE,
                locale,
                name=state_data.collected_data.child_name,
                age_months=round(results.get("age_months", 0), 1),
                corrected_note=corrected_note,
                total_questions=close_response.total_questions,
                overall_status=results.get("overall_status", "On track"),
                results_url=results_url
            )

            await whapi_client.send_link(phone, completion_msg, results_url)

            # Update state
            state_data.current_step = ConversationState.COMPLETED
            await self.save_state(phone, state_data)

        except Exception as e:
            logger.error(f"Failed to complete assessment for {phone}: {e}")
            locale = state_data.collected_data.locale or "en"
            error_msg = templates.get_message(templates.ERROR_MESSAGES, locale)
            await whapi_client.send_text(phone, error_msg)

    async def send_question_with_buttons(
        self,
        phone: str,
        question_text: str,
        locale: str,
        question_number: int
    ):
        """Send a question with answer buttons."""
        # Add progress indicator
        progress = templates.get_message(
            templates.QUESTION_PROGRESS,
            locale,
            current=question_number,
            total=12
        )

        full_message = f"{progress}\n\n{question_text}"

        # Get buttons for locale
        buttons = templates.ANSWER_BUTTONS.get(locale, templates.ANSWER_BUTTONS["en"])

        await whapi_client.send_buttons(phone, full_message, buttons)

    async def handle_completed_session(self, phone: str, state_data: ConversationStateData):
        """Handle messages after assessment is complete."""
        locale = state_data.collected_data.locale or "en"
        results_url = f"https://brainytots.com/pages/assessment-results?session_id={state_data.session_id}"

        msg = f"Your assessment is already complete! View results here:\n{results_url}\n\nType 'restart' to start a new assessment."
        await whapi_client.send_text(phone, msg)

    async def restart_conversation(self, phone: str):
        """Restart the conversation from beginning."""
        # Clear existing state
        await self.clear_state(phone)

        # Start fresh
        state_data = await self.get_or_create_state(phone, "User")
        await self.handle_new_user(phone, state_data)

    async def send_help(self, phone: str):
        """Send help message."""
        # Try to get user's locale from existing state
        state_data = await self.get_state(phone)
        locale = "en"
        if state_data and state_data.collected_data.locale:
            locale = state_data.collected_data.locale

        help_msg = templates.get_message(templates.HELP_MESSAGES, locale)
        await whapi_client.send_text(phone, help_msg)

    # ========== State Management ==========

    async def get_or_create_state(self, phone: str, user_name: str) -> ConversationStateData:
        """Get existing state or create new one."""
        existing = await state_store.get(phone)
        if existing:
            return existing

        state = ConversationStateData(
            current_step=ConversationState.NEW,
            last_message_at=datetime.utcnow()
        )
        await state_store.set(phone, state)
        return state

    async def get_state(self, phone: str) -> Optional[ConversationStateData]:
        """Get existing state."""
        return await state_store.get(phone)

    async def save_state(self, phone: str, state_data: ConversationStateData):
        """Save conversation state."""
        state_data.last_message_at = datetime.utcnow()
        await state_store.set(phone, state_data)
        logger.info(f"Saved state for {phone}: {state_data.current_step}")

    async def clear_state(self, phone: str):
        """Clear conversation state."""
        await state_store.delete(phone)
        logger.info(f"Cleared state for {phone}")

    # ========== Utility Methods ==========

    def parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string in various formats and return ISO format.

        Supports: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, etc.

        Returns:
            ISO format date (YYYY-MM-DD) or None if invalid
        """
        try:
            # Try common formats
            for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d"]:
                try:
                    dt = datetime.strptime(date_str.strip(), fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            # Try dateutil parser as fallback
            dt = date_parser.parse(date_str, dayfirst=True)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None
