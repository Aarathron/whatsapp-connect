import unittest
from datetime import datetime, timezone

from src.models import WhapiWebhookPayload


class WhapiWebhookPayloadTest(unittest.TestCase):
    def test_accepts_status_update_only(self):
        payload = WhapiWebhookPayload(
            event={"type": "messages", "event": "post"},
            channel_id="test-channel",
            statuses=[
                {
                    "id": "msg-1",
                    "status": "delivered",
                    "timestamp": int(datetime.now(timezone.utc).timestamp()),
                    "recipient_id": "12345"
                }
            ]
        )

        self.assertIsNone(payload.messages)
        self.assertEqual(payload.statuses[0]["status"], "delivered")

    def test_parses_buttons_reply_payload(self):
        payload = WhapiWebhookPayload(
            event={"type": "messages", "event": "post"},
            channel_id="test-channel",
            messages=[
                {
                    "id": "abc",
                    "from_me": False,
                    "type": "reply",
                    "chat_id": "123@s.whatsapp.net",
                    "timestamp": 1234567890,
                    "from": "123",
                    "reply": {
                        "type": "buttons_reply",
                        "buttons_reply": {
                            "id": "btn_0",
                            "title": "English"
                        }
                    }
                }
            ]
        )

        message = payload.messages[0]
        self.assertEqual(message.reply.buttons_reply.title, "English")


if __name__ == "__main__":
    unittest.main()

