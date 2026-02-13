# crontab -e
# chmod +x schedule_morning.sh
# 30 7 * * 1-5 bash /home/ubuntu/schedule_morning.sh >> /home/ubuntu/cron.log 2>&1
cd /home/ubuntu/services/train_time_check/.ubuntu

../venv/bin/python reusable_check.py \
 --target_station="金山" \
 --direction="down" \
 --range="6" \
 --enable_error_notification