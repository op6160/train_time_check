# typing
from src.model.model import TrainStatusModel

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from src.constants.notify_map import notify_ja_map, notify_en_map, notify_ko_map
from src.libs import logger
from src.notification.DiscordManager import DiscordManager
from src.utility import list_to_multiline


def set_notify_map(language):
    if language == "ja" or language == "jp":
        if language == "jp": logger.warning("The 'jp' language is deprecated. Please use 'ja' instead.")
        return notify_ja_map
    elif language == "en":
        return notify_en_map
    elif language == "ko" or language == "kr":
        if language == "kr": logger.warning("The 'kr' language is deprecated. Please use 'ko' instead.")
        return notify_ko_map
    else:
        logger.error(f"Unsupported language: {language}")
        sys.exit(1)

def send_delay_notification(webhook_url: str, language: str, train_status: TrainStatusModel):
    """
    Formats and sends a train delay notification.
    """
    # set notify map
    notify_map = set_notify_map(language)
    # ini discord manager
    discord = DiscordManager(webhook_url)

    # get train messages
    train_messages = train_status.train_message
    multiline_train_message = list_to_multiline(train_messages)

    if not multiline_train_message:
        logger.info("Delay status detected, but no relevant trains or notices found in range. Skipping notification.")
        return

    # 
    notice_case = notify_map['delay_sender']
    notice_msg = train_status.notice_message
    
    # message parts
    alert_title = notify_map['alert_title']
    train_list = notify_map['train_list']
    status_info = notify_map['status_info']

    logger.info("Delay detected! Sending notification...")
    # compose message
    full_message = \
f"""❗{alert_title}
[{train_list}]
{multiline_train_message}"""
    if notice_msg:
        full_message += \
f"""\n\n[{status_info}]
{notice_msg}"""
    full_message += "\n" + datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%H:%M:%S") + "\n"

    discord.send_message(full_message, notice_case)
    return

def send_error_notification(webhook_url, language, error, traceback_details):
    """
    Formats and sends a script error notification.
    """
    notify_map = set_notify_map(language)
    discord = DiscordManager(webhook_url)
    
    error_message = f"⚠️ {notify_map['error_occured']}\n\n{str(error)}"
    error_details_payload = f"traceback: {traceback_details}"
    
    discord.send_message(error_message + error_details_payload, notify_map['script_error_sender'])
