import os
import sys
import traceback

from src.api import get_train_status_range_api
from src.libs import logger
from src.notification.notify import send_delay_notification, send_error_notification

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

    # execute
    try:
        result = check_train_status(target_station, direction, range_n, language)
        
        if result["status"] == "delay":
            send_delay_notification(webhook_url, language, result)
        else:
            logger.info("Status is normal. No notification sent.")

    except Exception as e:
        logger.error("An unexpected error occurred.", exc_info=True)
        if enable_error_notify:
            error_details = traceback.format_exc()
            send_error_notification(webhook_url, language, e, error_details)
        sys.exit(1)

if __name__ == "__main__":
    main()
