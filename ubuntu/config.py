# config.py
# you can set your webhook url and github token.
# if you want to use .env, just set use_env = True
use_env = True

# === set your webhook url and github token directly from here === #
# if you don't want to use webhook notice, set webhook_url = ""
webhook_url = "set your webhook url here"

# support development
# if send_issues is True, you can set your github token.
send_issues = False
github_token = "set your github token here"
# you can check your url and token by executing this script.
# ================================================== #
# check config
if use_env:
    print("[config] Use .env")
    import os
    import dotenv
    
    dotenv.load_dotenv()

    webhook_url = os.getenv("WEBHOOK_URL") or os.getenv("webhook_url")
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("github_token")
    send_issues = os.getenv("SEND_ISSUES") or os.getenv("send_issues")
    
    send_issues = True if send_issues == "True" else False
    if webhook_url is None:
        raise RuntimeError("[config Error] Webhook URL is not set in .env.")
    elif send_issues and github_token is None:
        raise RuntimeError("[config Error] If you want to send issues, Github Token must be set in .env.")
else:
    if webhook_url == "set your webhook url here":
        raise RuntimeError("[config Error] Webhook URL is not set in config.py.")
    if send_issues and github_token == "set your github token here":
        raise RuntimeError("[config Error] If you want to send issues, Github Token must be set in config.py.")

# validation
def _validate_webhook_discord():
    import requests
    response = requests.get(webhook_url)
    if response.status_code == 200:
        data = response.json()
        if "type" in data and "channel_id" in data:
                return True

def _validate_github_token():
    import requests
    try:
        response = requests.get("https://api.github.com/user", headers={"Authorization":f"token {github_token}", "Accept": "application/vnd.github.v3+json"})
        if response.status_code == 401:
            print("[Github Token Error] Invalid token")
            return False
        if response.status_code == 200:
            user_data = response.json()
            username = user_data["login"]

            scopes = response.headers.get("X-Oauth-Scopes", "")
            print(f"[Gihtub Token] Token confirms use: {username}")
            print(f"[Gihtub Token] Scopes: {scopes}")
            if "repo" in scopes or "public_repo" in scopes:
                return True
            else:
                print("[Github Token Error] Token does not have 'repo' or 'public_repo' scopes.")
                return False
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if _validate_webhook_discord():
        print("[Valid] Webhook url confirmed (No message sent).")
    else:
        print("[config Error] Discord Webhook URL is not valid.")
    
    if _validate_github_token():
        print("[Valid] Github Token confirmed (No message sent).")
    else:
        print("[config Error] Github Token is not valid.")