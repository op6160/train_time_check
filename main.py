# typing
from src.model.model import TrainStatusModel

import os
import sys
import traceback

from src.contents.get_contents import get_train_status_range
from src.libs import logger
from src.notification.notify import send_delay_notification, send_error_notification

def check_train_status(target_station, direction, range_n, language) -> TrainStatusModel:
    """
    train status check & call out train status function
    """
    logger.info(f"Checking train status for {target_station} ({direction})...")
    return get_train_status_range(
        station=target_station,
        range_n=range_n,
        language=language,
        direction=direction
    )

def error_handler(
    enable_error_notify: bool, 
    webhook_url: str, 
    language: str, 
    error: Exception = None, 
    error_message: str = "An unexpected error occurred."
    ):
    logger.error(error_message, exc_info=True)
    if enable_error_notify:
        error_details = traceback.format_exc()
        send_error_notification(webhook_url, language, error, error_details)
    sys.exit(1)
    return

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

    # execute
    try:
        result = check_train_status(target_station, direction, range_n, language)
        
        if result.status == "delay":
            send_delay_notification(webhook_url, language, result)
        elif result.status == "normal":
            logger.info(result.status_message)
        else:
            logger.info(result.status_message)

    except Exception as e:
        error_handler(
            enable_error_notify,
            webhook_url,
            language,
            error=e,
            error_message="An unexpected error occurred."
        )

if __name__ == "__main__":
    main()
