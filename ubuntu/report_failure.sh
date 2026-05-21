#!/bin/bash 

# init path
cd "$(dirname "$0")"
PROJECT_ROOT=".."
LOG_FILE="~/cron.log"
ISSUE_BODY="issue_body.md"

# init repo info
REPO_URL=$(git -C "$PROJECT_ROOT" config --get remote.origin.url)
REPO_NAME=$(basename -s .git "$REPO_URL")
REPO_OWNER=$(basename $(dirname "$REPO_URL"))
FULL_REPO="$REPO_OWNER/$REPO_NAME"

HOSTNAME=$(hostname)
CURRENT_TIME=$(date +'%Y-%m-%d %H:%M:%S')

# ---------------------------------------------------------
# get error type
# ---------------------------------------------------------
# 로그 파일의 '비어있지 않은 마지막 줄'
# 예: "ConnectionError: Max retries exceeded..."
if [ -f "$LOG_FILE" ]; then
    # tail로 끝을 잡고, 공백 라인 제거 후, 마지막 1줄만 추출. 너무 길면 앞 60자만 자름.
    ERROR_SIGNATURE=$(tail -n 10 "$LOG_FILE" | grep -v "^$" | tail -n 1 | cut -c 1-60)
else
    ERROR_SIGNATURE="Unknown Error (No Log)"
fi

ISSUE_TITLE_PREFIX="⚠️ Train Check Failed"
SPECIFIC_ISSUE_TITLE="$ISSUE_TITLE_PREFIX: $ERROR_SIGNATURE"

# ---------------------------------------------------------
# exist issue check
# ---------------------------------------------------------
echo "🔍 Checking for existing issue with signature: $ERROR_SIGNATURE"

# search error type, opened eror
EXISTING_ISSUE_URL=$(gh issue list \
    --repo "$FULL_REPO" \
    --search "\"$SPECIFIC_ISSUE_TITLE\" in:title" \
    --state open \
    --limit 1 \
    --json url \
    --jq '.[0].url')

# ---------------------------------------------------------
# if issue exist
# ---------------------------------------------------------

if [ -n "$EXISTING_ISSUE_URL" ]; then
    # issue exist : cooment
    echo "✅ Found existing issue for this specific error: $EXISTING_ISSUE_URL"
    
    COMMENT_BODY="**Recurrence:** $CURRENT_TIME (JST) on $HOSTNAME"
    gh issue comment "$EXISTING_ISSUE_URL" --body "$COMMENT_BODY"
    
    # exit (skip webhook)
    exit 0

else
    # new error type: create issue
    echo "🆕 New error type detected. Creating a new issue..."

    echo "### ⚠️ Workflow Failure Report" > "$ISSUE_BODY"
    echo "**Error Type:** \`$ERROR_SIGNATURE\`" >> "$ISSUE_BODY"
    echo "**Server:** $HOSTNAME" >> "$ISSUE_BODY"
    echo "**Time:** $CURRENT_TIME (JST)" >> "$ISSUE_BODY"
    echo "" >> "$ISSUE_BODY"
    echo "**Recent Log Output:**" >> "$ISSUE_BODY"
    echo "\`\`\`" >> "$ISSUE_BODY"
    if [ -f "$LOG_FILE" ]; then
        tail -n 30 "$LOG_FILE" >> "$ISSUE_BODY"
    fi
    echo "\`\`\`" >> "$ISSUE_BODY"

    # create issue
    ISSUE_URL=$(gh issue create \
        --repo "$FULL_REPO" \
        --title "$SPECIFIC_ISSUE_TITLE" \
        --body-file "$ISSUE_BODY" \
        --label "bug")

    echo "Created Issue: $ISSUE_URL"

    # discord web hook
    if [ -n "$WEBHOOK_URL" ]; then
        DISCORD_MSG="🚨 **New Error Detected**\n새로운 유형의 에러가 발생했습니다:\n\`$ERROR_SIGNATURE\`\n$ISSUE_URL"
        
        curl -H "Content-Type: application/json" \
             -d "{\"content\": \"$DISCORD_MSG\", \"username\": \"Train Server Error Bot\"}" \
             "$WEBHOOK_URL"
    fi

    rm "$ISSUE_BODY"
fi