from src.libs import logger
import requests

class DiscordManager:
    def __init__(self, webhook_url: str):
        if not webhook_url:
            raise ValueError("DiscordManager requires 'webhook_url'.")
        self.webhook_url = webhook_url

    def send_message(self, message: str, notice_case: str):
        url = self.webhook_url

        payload = {
            "content": message,
            "username": notice_case
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Notification sent successfully: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
        return None
