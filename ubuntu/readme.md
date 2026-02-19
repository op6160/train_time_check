Github Actions의 cron 동작이 불안정하기 때문에, 안정성, 지속성의 문제가 발생, 보유한 리소스를 활용하여 ubuntu OS의 crontab 기능을 사용하기 위해서 ubuntu용 python script를 작성

Github Actions の cron 動作の不安定を回避するため、保有するサーバーリソースを使用、ubuntu OS の crontab を使用するために, ubuntu 用 python script を作成

## setup
Python 3.9+

* If server is ARM architecture, required
```bash
sudo apt update
sudo apt install chromium-browser chromium-chromedriver
```

The chromedrive path required ```'/usr/bin/chromedriver'``` (default path)
> ※ It is defined in the utility_python submodule.

clone repository:
```git clone --recurse-submodules https://github.com/op6160/train_time_check.git```  <br>

install requirements:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

set file permission:
```bash
cd train_time_check/ubuntu
chmod +x schedule_evening.sh
chmod +x schedule_morning.sh
```
write config.py:
#### 1. write directly   <br>
   webhook url (required)
```python
webhook_url = "set your webhook url here"
```

   github token (optional)
```python
send_issues = True
github_token = "set your github token here"
```
If you want to send issues, you should set github token.

#### 2. use dotenv (recommended)
```python
use_env = True
```
<br>

```/ubuntu/.env``` required
```.env
webhook_url = "set your webhook url here"
GITHUB_TOKEN = "set your github token here"
SEND_ISSUES = "True"
```

## usage e.g.,
Execute Directly:
```bash
venv/bin/python -m ubuntu.reusable_check.py \
 --target_station="刈谷" \
 --direction="up" \
 --range="6" \
 --language="en"
```

Use Bourne Shell
```./ubuntu/schedule_morning.sh```

Set Cron Table Automation:
```crontab -e```

[cron set manual](https://www.ibm.com/docs/en/aix/7.3.0?topic=c-crontab-command)

```bash
30 17 * * 1-5 bash ~/services/train_time_check/ubuntu/schedule_evening.sh >> /home/ubuntu/cron.log 2>&1
45 17 * * 1-5 bash ~/services/train_time_check/ubuntu/schedule_evening.sh >> /home/ubuntu/cron.log 2>&1

30 7 * * 1-5 ~/services/train_time_check/ubuntu/schedule_morning.sh >> /home/ubuntu/cron.log 2>&1
00 8 * * 1-5 ~/services/train_time_check/ubuntu/schedule_morning.sh >> /home/ubuntu/cron.log 2>&1
```