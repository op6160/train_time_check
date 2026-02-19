# crontab -e
# chmod +x schedule_morning.sh
# 30 7 * * 1-5 bash /home/ubuntu/schedule_morning.sh >> /home/ubuntu/cron.log 2>&1
cd /home/ubuntu/services/train_time_check
venv/bin/python -m ubuntu.reusable_check \
 --target_station="金山" \
 --direction="down" \
 --range="6" \
 --enable_error_notification \
 --language="ko"