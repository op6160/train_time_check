import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from src.notification.constants import notify_ja_map, notify_en_map, notify_ko_map
from src.libs import logger
from src.DiscordManager import DiscordManager

def set_language_map(language):
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

def get_clean_train_msg_from_result(result):
    train_msgs_list = result.get("train_messages", [])
    return "\n".join(train_msgs_list)

def send_delay_notification(webhook_url, language, result):
    """
    Formats and sends a train delay notification.
    """
    language_map = set_language_map(language)
    discord = DiscordManager(webhook_url)

    train_msgs = get_clean_train_msg_from_result(result)

    if not train_msgs:
        logger.info("Delay status detected, but no relevant trains or notices found in range. Skipping notification.")
        return

    notice_case = language_map['delay_sender']
    notice_msg = result.get("notice_message", "")

    logger.info("Delay detected! Sending notification...")
    full_message = \
f"""❗{language_map['alert_title']}
[{language_map['train_list']}]
{train_msgs}"""
    if notice_msg:
        full_message += \
f"""\n\n[{language_map['status_info']}]
{notice_msg}"""
    full_message += "\n" + datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%H:%M:%S") + "\n"

    discord.send_message(full_message, notice_case)

def send_error_notification(webhook_url, language, error, traceback_details):
    """
    Formats and sends a script error notification.
    """
    language_map = set_language_map(language)
    discord = DiscordManager(webhook_url)
    
    error_message = f"⚠️ {language_map['error_occured']}\n\n{str(error)}"
    error_details_payload = {"traceback": traceback_details}
    
    discord.send_message(error_message + error_details_payload, language_map['script_error_sender'])
