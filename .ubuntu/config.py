# config.py
# you can set your webhook url and github token.

# === set your webhook url and github token here === #
# if you don't want to use webhook notice, set webhook_url = ""
webhook_url = "set your webhook url here"
send_issues = True

# if send_issues is True, you can set your github token.
github_token = "set your github token here"

# ================================================== #

# check
if webhook_url == "set your webhook url here":
    raise RuntimeError("[config.py Error] Webhook URL is not set in config.py.")
if send_issues and github_token == "set your github token here":
    raise RuntimeError("[config.py Error] If you want to send issues, Github Token must be set in config.py.")

# if github_token == "set your github token here":
#     raise RuntimeError("[config.py Error] Github Token is not set in config.py.")

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
        print("[Error] Discord Webhook URL is not valid.")
    
    if _validate_github_token():
        print("[Valid] Github Token confirmed (No message sent).")
    else:
        print("[Error] Github Token is not valid.")