import os
import unittest
from unittest.mock import AsyncMock, patch


# Seed environment variables before importing application modules so that
# Pydantic settings construction succeeds and memory-only state storage is allowed.
os.environ.setdefault("WHAPI_API_TOKEN", "test-token")
os.environ.setdefault("WHAPI_CHANNEL_ID", "test-channel")
os.environ.setdefault("WHATSAPP_NUMBER", "0000000000")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ALLOW_MEMORY_STATE_STORE", "1")


from src.conversation_flow import ConversationFlowHandler  # noqa: E402
from src.models import ConversationState  # noqa: E402
from src.state_store import state_store  # noqa: E402


class ConversationFlowRegressionTest(unittest.IsolatedAsyncioTestCase):
    """Regression tests for early conversation steps."""

    def setUp(self) -> None:
        self.phone = "15551234567"
        self.parent_name = "Alex"

        self.buttons_patcher = patch(
            "src.conversation_flow.whapi_client.send_buttons",
            new=AsyncMock()
        )
        self.text_patcher = patch(
            "src.conversation_flow.whapi_client.send_text",
            new=AsyncMock()
        )

        self.mock_send_buttons = self.buttons_patcher.start()
        self.mock_send_text = self.text_patcher.start()

        self.flow_handler = ConversationFlowHandler(db=None)

    async def asyncTearDown(self) -> None:
        await state_store.delete(self.phone)
        self.buttons_patcher.stop()
        self.text_patcher.stop()

    async def test_language_then_name_transitions_to_dob_prompt(self) -> None:
        # Start conversation -> expect welcome buttons and LANGUAGE_SELECT state
        await self.flow_handler.handle_message(self.phone, self.parent_name, "Start")

        state_after_start = await state_store.get(self.phone)
        self.assertIsNotNone(state_after_start)
        self.assertEqual(state_after_start.current_step, ConversationState.LANGUAGE_SELECT)
        self.mock_send_buttons.assert_awaited_once()

        # Select language -> expect locale set and ASK_NAME state
        await self.flow_handler.handle_message(self.phone, self.parent_name, "English")

        state_after_language = await state_store.get(self.phone)
        self.assertIsNotNone(state_after_language)
        self.assertEqual(state_after_language.collected_data.locale, "en")
        self.assertEqual(state_after_language.current_step, ConversationState.ASK_NAME)
        self.assertEqual(self.mock_send_text.await_count, 1)

        # Provide child's name -> expect ASK_DOB and name preserved
        await self.flow_handler.handle_message(self.phone, self.parent_name, "Sia")

        state_after_name = await state_store.get(self.phone)
        self.assertIsNotNone(state_after_name)
        self.assertEqual(state_after_name.collected_data.child_name, "Sia")
        self.assertEqual(state_after_name.current_step, ConversationState.ASK_DOB)
        self.assertEqual(self.mock_send_text.await_count, 2)


if __name__ == "__main__":
    unittest.main()

