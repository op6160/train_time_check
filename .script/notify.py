import os
import sys
import json
import requests
import logging
import traceback
from datetime import datetime

# src import
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
src_path = os.path.join(root_dir, "src")
sys.path.append(src_path)
sys.path.append(root_dir)

from api import get_train_status_range_api

# 로거 설정
logger = logging.getLogger("TrainCheck")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 파일 로거 추가 (workflow/logs)
log_dir = os.path.join(current_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

today_str = datetime.now().strftime("%Y-%m-%d")
log_filename = f"train_check_{today_str}.log"

file_handler = logging.FileHandler(os.path.join(log_dir, log_filename), encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

def send_webhook(url, message, notice_case="열차지연", detail=None):
    """
    Webhook URL 데이터, 메시지 전송
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

def check_train_status(target_station, direction, range_n):
    """
    열차 상태 확인 api 값 반환
    """
    logger.info(f"Checking train status for {target_station} ({direction})...")
    return get_train_status_range_api(
        station=target_station,
        range_n=range_n,
        language="ko",
        direction=direction
    )

def main():
    # 설정값 로드
    webhook_url = os.environ.get("WEBHOOK_URL")
    target_station = os.environ.get("TARGET_STATION", "刈谷")
    direction = os.environ.get("DIRECTION", "up")
    range_n = int(os.environ.get("RANGE_N", 6))
    enable_error_notify = os.environ.get("ENABLE_ERROR_NOTIFICATION", "true").lower() == "true"
    
    if webhook_url is None:
        logger.error("WEBHOOK_URL environment variable is not set.")
        sys.exit(1)

    try:
        result = check_train_status(target_station, direction, range_n)

        if result["status"] == "delay":
            notice_msg = result.get("notice_message", "")
            train_msgs_list = result.get("train_messages", [])
            train_msgs = "\n".join(train_msgs_list)

            if not train_msgs:
                logger.info("Delay status detected, but no relevant trains or notices found in range. Skipping notification.")
                return

            logger.info("Delay detected! Sending notification...")
            full_message = f"❗열차 지연 발생\n[지연 열차 목록]\n{train_msgs}\n\n[운행 정보]\n{notice_msg}"
            
            send_webhook(webhook_url, full_message, "열차 지연" , result["raw_data"])
        else:
            logger.info("Status is normal. No notification sent.")

    except Exception as e:
        logger.error("An unexpected error occurred.", exc_info=True)
        
        if enable_error_notify:
            error_message = f"⚠️ 열차 확인 스크립트 에러 발생\n\n{str(e)}"
            error_details = {"traceback": traceback.format_exc()}
            send_webhook(webhook_url, error_message, "스크립트 에러", error_details)
        
        sys.exit(1)

if __name__ == "__main__":
    main()