# crontab -e
# chmod +x schedule_evening.sh
# 30 17 * * 1-5 bash /home/ubuntu/schedule_evening.sh >> /home/ubuntu/cron.log 2>&1
cd /home/ubuntu/services/train_time_check/.ubuntu 
../venv/bin/python reusable_check.py \
 --target_station="刈谷" \
 --direction="up" \
 --range="6" \
 --enable_error_notification \
 --language="ko"