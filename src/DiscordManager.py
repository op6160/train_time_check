from src.libs import save_content, load_content, DiscordStrategy
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

class DiscordBot(DiscordManager):
    def __init__(self, bot_token: str, channel_id: str, webhook_url: str):
        super().__init__(webhook_url)

        if not bot_token or not channel_id:
            raise ValueError("DiscordManager requires 'bot_token' and 'channel_id'.")

        self.bot_token = bot_token
        self.channel_id = channel_id

        self.drive_strategy = DiscordStrategy( 
            bot_token=self.bot_token, 
            channel_id=self.channel_id
        )

    def save_content(self, content, filename):
        save_content(content, filename, self.drive_strategy)

    def load_content(self, filename):
        return load_content(filename, self.drive_strategy)
