from config import webhook_url, github_token, send_issues

import os
import sys
import argparse
import subprocess
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))

venv_path = base_dir / "venv"
if not os.path.exists(venv_path):
    try:
        subprocess.run(["python3", "-m", "venv", str(venv_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[reusable_check Error] Failed to create virtual environment: {e}")
        sys.exit(1)
    try:
        subprocess.run([str(venv_path / "bin" / "python"), "-m", "pip", "install", "-r", f"{base_dir}/requirements.txt"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[reusable_check Error] Failed to install requirements: {e}")
        sys.exit(1)

venv_python = venv_path / "bin" / "python"

notify_path = base_dir / ".script" / "notify.py"
fail_script = base_dir / ".script" / "report_failure.sh"

parser = argparse.ArgumentParser(
    description="Reusable Train Check",
    epilog="Example: python reusable_check.py -s 刈谷 -d up -r 6 -e true"
)

parser.add_argument("-s", "--target_station", type=str, required=True, help="Target station to monitor")
parser.add_argument("-d", "--direction", type=str, required=True, help="Direction of the train")
parser.add_argument("-r", "--range", type=int, default=6, help="Range of stations to check")
parser.add_argument("-e", "--enable_error_notification", action="store_true", help="Enable error notifications")

args = parser.parse_args()
env_vars = os.environ.copy()
env_vars.update({
    "WEBHOOK_URL": webhook_url,
    "TARGET_STATION": args.target_station,
    "DIRECTION": args.direction,
    "RANGE": str(args.range),
    "ENABLE_ERROR_NOTIFICATION": str(args.enable_error_notification).lower()
})

print(f"[Commute Check] Start workflow. Target Station: {args.target_station}, Direction: {args.direction}, Range: {args.range}, Enable Error Notification: {args.enable_error_notification}")

try:
    subprocess.run([venv_python, notify_path],env=env_vars,check=True,text=True)
    print(f"[Commute Check] Workflow completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"[Commute Check] Workflow failed with error: {e}")
    if os.path.exists(fail_script) and send_issues:
        env_vars.update({"GH_TOKEN": github_token})
        print(f"[Commute Check] Running failure script: {fail_script}")
        subprocess.run(["bash", fail_script],
        env=env_vars,
        check=True,text=True)
    else:
        print(f"[Reusable Check Error] Failure script not found: {fail_script}")
    
    sys.exit(1)

