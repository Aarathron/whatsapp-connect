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


if __name__ == "__main__":
    unittest.main()

