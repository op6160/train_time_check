#!/bin/bash

# find log
LOG_FILE=$(ls -t workflow/logs/*.log 2>/dev/null | head -n 1)
ISSUE_BODY="issue_body.md"

# write github issues
echo "### Workflow Failure Details" > "$ISSUE_BODY"
echo "The scheduled train check workflow failed." >> "$ISSUE_BODY"
echo "**Log Output:**" >> "$ISSUE_BODY"
echo "\`\`\`" >> "$ISSUE_BODY"

if [ -f "$LOG_FILE" ]; then
    cat "$LOG_FILE" >> "$ISSUE_BODY"
else
    echo "Log file not found." >> "$ISSUE_BODY"
fi

echo "\`\`\`" >> "$ISSUE_BODY"
echo "View Workflow Run: $GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID" >> "$ISSUE_BODY"

# GitHub CLI issue report
CURRENT_TIME=$(date +'%Y-%m-%d %H:%M')
ISSUE_URL=$(gh issue create --title "⚠️ Train Check Workflow Failed ($CURRENT_TIME)" --body-file "$ISSUE_BODY" --label "bug")

echo "Created Issue: $ISSUE_URL"

# Discord webhook notification
if [ -n "$WEBHOOK_URL" ]; then
    curl -H "Content-Type: application/json" \
         -d "{\"content\": \"⚠️ **Workflow Failed**\n에러 로그가 이슈로 등록되었습니다:\n$ISSUE_URL\", \"username\": \"Train Delay Checker Error\"}" \
         "$WEBHOOK_URL"
fi