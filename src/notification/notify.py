# src import
import os
import sys

from src.api import get_train_status_range_api
from src.notification.constants import notify_ja_map, notify_en_map, notify_ko_map
from src.libs import logger
from src.DiscordManager import DiscordManager

import json
import requests
import traceback
from datetime import datetime

def check_train_status(target_station, direction, range_n, language):
    """
    train status check & call API
    """
    logger.info(f"Checking train status for {target_station} ({direction})...")
    return get_train_status_range_api(
        station=target_station,
        range_n=range_n,
        language=language,
        direction=direction
    )

def set_language_map(language):
    if language == "ja" or language == "jp":
        if language == "ja": logger.warning("The 'jp' language is deprecated. Please use 'ja' instead.")
        language_map = notify_ja_map
    elif language == "en":
        language_map = notify_en_map
    elif language == "ko" or language == "kr":
        if language == "kr": logger.warning("The 'kr' language is deprecated. Please use 'ko' instead.")
        language_map = notify_ko_map
    else:
        logger.error(f"Unsupported language: {language}")
        sys.exit(1)
    return language_map

def get_clean_train_msg_from_result(result):
    train_msgs_list = result.get("train_messages", [])
    return "\n".join(train_msgs_list)

def main():
    # load env 
    webhook_url = os.environ.get("WEBHOOK_URL")
    target_station = os.environ.get("TARGET_STATION", "刈谷")
    direction = os.environ.get("DIRECTION", "up")
    range_n = int(os.environ.get("RANGE_N", 6))
    language = os.environ.get("LANGUAGE", "ko")
    enable_error_notify = os.environ.get("ENABLE_ERROR_NOTIFICATION", "true").lower() == "true"
    
    if webhook_url is None:
        logger.error("WEBHOOK_URL environment variable is not set.")
        sys.exit(1)

    # set language map
    set_language_map(language)

    # execute
    try:
        result = check_train_status(target_station, direction, range_n, language)
        
        if result["status"] == "delay":
            train_msgs = get_clean_train_msg_from_result(result)

            if not train_msgs:
                logger.info("Delay status detected, but no relevant trains or notices found in range. Skipping notification.")
                return

            notice_case = language_map['delay_sender']
            notice_msg = result.get("notice_message", "")
            # detail = result['raw_data']

            logger.info("Delay detected! Sending notification...")
            full_message = \
                f"""❗{language_map['alert_title']}
                [{language_map['train_list']}]
                {train_msgs}"""
            if notice_msg:
                full_message += \
                    f"""\n\n[{language_map['status_info']}]
                    {notice_msg}"""

            discord = DiscordManager(webhook_url)
            discord.send_message(full_message, notice_case)
        else:
            logger.info("Status is normal. No notification sent.")

    except Exception as e:
        logger.error("An unexpected error occurred.", exc_info=True)
        
        if enable_error_notify:
            error_message = f"⚠️ {language_map['error_occured']}\n\n{str(e)}"
            error_details = {"traceback": traceback.format_exc()}
            send_webhook(webhook_url, error_message, language_map['script_error_sender'], error_details)
        sys.exit(1)

if __name__ == "__main__":
    main()