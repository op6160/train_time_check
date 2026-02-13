Github Actions의 cron 기능이 불안정하기 때문에
 (가능한 경우) 리소스를 활용하여 ubuntu 서버의 cron 기능을 사용하기 위해서 ubuntu script를 작성

=====

 ## usage
clone repository:
```git clone --recurse-submodules https://github.com/op6160/train_time_check.git```
set file permission:

```
cd train_time_check/.ubuntu
chmod +x schedule_evening.sh
chmod +x schedule_morning.sh
```

set cron table:
```crontab -e```
```
30 17 * * 1-5 bash ~/services/train_time_check/.ubuntu/schedule_evening.sh >> /home/ubuntu/cron.log 2>&1
45 17 * * 1-5 bash ~/services/train_time_check/.ubuntu/schedule_evening.sh >> /home/ubuntu/cron.log 2>&1

30 7 * * 1-5 ~/services/train_time_check/.ubuntu/schedule_morning.sh >> /home/ubuntu/cron.log 2>&1
00 8 * * 1-5 ~/services/train_time_check/.ubuntu/schedule_morning.sh >> /home/ubuntu/cron.log 2>&1
```