import os
import unittest


# Seed required environment variables before importing the client so that
# pydantic settings construction succeeds during module import.
os.environ.setdefault("WHAPI_API_TOKEN", "dummy-token")
os.environ.setdefault("WHAPI_CHANNEL_ID", "dummy-channel")
os.environ.setdefault("WHATSAPP_NUMBER", "0000000000")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


from src.whapi_client import WhapiClient  # noqa: E402  (import after env seed)


class WhapiButtonPayloadTest(unittest.TestCase):
    def setUp(self) -> None:
        # Bypass __init__ so we do not depend on network configuration.
        self.client = WhapiClient.__new__(WhapiClient)

    def test_button_payload_matches_whapi_schema(self) -> None:
        payload = self.client._build_button_payload(
            phone="1234567890",
            body="Choose an option",
            buttons=["Yes", "No"]
        )

        self.assertEqual(payload["type"], "button")
        self.assertEqual(payload["body"]["text"], "Choose an option")

        action = payload["action"]
        self.assertIn("buttons", action)

        buttons = action["buttons"]
        self.assertEqual(len(buttons), 2)

        first_button = buttons[0]
        self.assertEqual(first_button["type"], "quick_reply")
        self.assertEqual(first_button["id"], "btn_0")
        self.assertEqual(first_button["title"], "Yes")


if __name__ == "__main__":
    unittest.main()

