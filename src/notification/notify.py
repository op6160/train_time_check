# src import
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from api import get_train_status_range_api
from notify_language_map import notify_ja_map, notify_en_map, notify_ko_map
from libs import logger

import os
import sys
import json
import requests
import traceback
from datetime import datetime

def send_webhook(url, message, notice_case="train delay", detail=None):
    """
    Webhook URL, send data& message.
    """
    if url is None:
        logger.warning("Webhook URL is not set. Skipping notification.")
        return

    payload = {
        "content": message,
        "username": notice_case
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Notification sent successfully: {response.status_code}")
    except Exception as e:
        if url == "":
            logger.info(f"Webhook url is empty. Sending notification is skipped.")
        else:
            logger.error(f"Failed to send notification: {e}")

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
    if language == "ja":
        language_map = notify_ja_map
    elif language == "en":
        language_map = notify_en_map
    elif language == "ko":
        language_map = notify_ko_map
    elif language == "jp":
        # jp -> ja
        language_map = notify_ja_map
        logger.warning("The 'jp' language is deprecated. Please use 'ja' instead.")
        language = "ja"
    elif language == "kr":
        # kr -> ko
        language_map = notify_ko_map
        logger.warning("The 'kr' language is deprecated. Please use 'ko' instead.")
        language = "ko"
    else:
        logger.error(f"Unsupported language: {language}")
        sys.exit(1)

    try:
        result = check_train_status(target_station, direction, range_n, language)

        if result["status"] == "delay":
            notice_msg = result.get("notice_message", "")
            train_msgs_list = result.get("train_messages", [])
            train_msgs = "\n".join(train_msgs_list)

            if not train_msgs:
                logger.info("Delay status detected, but no relevant trains or notices found in range. Skipping notification.")
                return

            logger.info("Delay detected! Sending notification...")
            full_message = f"❗{language_map['alert_title']}\n[{language_map['train_list']}]\n{train_msgs}\n\n[{language_map['status_info']}]\n{notice_msg}"
            
            send_webhook(webhook_url, full_message, language_map['delay_sender'] , result['raw_data'])
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