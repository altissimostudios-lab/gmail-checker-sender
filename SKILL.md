# Gmail Checker Sender

Send emails and replies via Gmail API with OAuth authentication.

## Features

- ✅ Send new emails
- ✅ Reply to threads (keeps conversation intact)
- ✅ Custom From address (e.g., hello@livemoments.com.sg)
- ✅ CC/BCC support
- ✅ Save as draft
- ✅ Preview before send (safety)
- ✅ JSON output for automation

## Setup

### 1. OAuth Credentials

Must have Gmail OAuth credentials set up:

```bash
# Credentials stored at:
~/.nanobot/credentials/gmail/{account}.token
```

Run setup from `gmail-checker` skill first if needed.

### 2. Python Dependencies

```bash
cd /Users/friday/.nanobot/workspace/skills/gmail-checker-sender
python3 -m venv venv
source venv/bin/activate
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Usage

### Send New Email

```bash
./send_email.py \
  --to "client@example.com" \
  --subject "Booking Confirmation" \
  --body "Your booking is confirmed!" \
  --from "hello@livemoments.com.sg"
```

### Reply to Thread

```bash
./send_email.py \
  --to "client@example.com" \
  --reply-to "THREAD_ID_HERE" \
  --reply-subject "Original Subject" \
  --body-file email_body.txt \
  --from "hello@livemoments.com.sg" \
  --cc "other@example.com"
```

### Save as Draft

```bash
./send_email.py \
  --to "client@example.com" \
  --subject "Draft Email" \
  --body "Draft content" \
  --draft
```

### Auto-Confirm (No Preview)

```bash
./send_email.py \
  --to "client@example.com" \
  --subject "Quick Send" \
  --body "Urgent message" \
  --yes
```

## CLI Reference

| Flag | Description | Required |
|------|-------------|----------|
| `--to` | Recipient email | ✅ Yes |
| `--subject` | Email subject | ✅ Yes (except replies) |
| `--body` | Email body text | Optional (use --body-file or stdin) |
| `--body-file` | File containing body | Optional |
| `--from` | From address override | Optional |
| `--cc` | CC recipients (comma-separated) | Optional |
| `--bcc` | BCC recipients (comma-separated) | Optional |
| `--reply-to` | Thread ID to reply to | Optional |
| `--reply-subject` | Original subject for replies | Required with --reply-to |
| `--draft` | Save as draft instead of sending | Optional |
| `--yes` | Auto-confirm without preview | Optional |
| `--json` | Output as JSON | Optional |
| `--account` | Gmail account to use | Optional (default: livemomentssg@gmail.com) |

## Workflow Examples

### Confirm Booking & Notify Designer

```bash
# 1. Send confirmation to client
./send_email.py \
  --reply-to "ABC123threadID" \
  --reply-subject "Wedding Booking" \
  --to "bride@example.com" \
  --body-file confirmation.txt \
  --from "hello@livemoments.com.sg"

# 2. Notify designer (separate email)
./send_email.py \
  --to "designer@livemoments.com.sg" \
  --subject "New Design Job - Wedding July 5" \
  --body-file designer_brief.txt
```

### Save Draft for Review

```bash
./send_email.py \
  --to "important@client.com" \
  --subject "Quote Request" \
  --body-file quote_draft.txt \
  --draft
```

## Safety Features

1. **Preview Before Send** - Always shows email before sending (unless --yes)
2. **Reply Threading** - Automatically handles In-Reply-To and References headers
3. **Custom From** - Supports send-as aliases configured in Gmail
4. **Draft Mode** - Review before committing

## Troubleshooting

### "No credentials found"
- Run OAuth setup from gmail-checker skill first
- Check credentials exist in `~/.nanobot/credentials/gmail/`

### "Message not delivered"
- Check spam folders
- Use reply-to-thread instead of new email for better deliverability
- Ensure custom From address is verified in Gmail settings

### Thread ID not working
- Get thread ID from Gmail URL: `#inbox/THREAD_ID_HERE`
- Ensure you're replying to the correct thread

## Requirements

- Python 3.7+
- Google API credentials with Gmail scope
- `gmail.modify` OAuth scope (for send + draft)

## Integration with Workflows

Combine with `gmail-checker` for full pipeline:

```bash
# 1. Check for new booking emails
./check_gmail.py --label "bookings"

# 2. Extract details and draft reply

# 3. Send via this skill
./send_email.py --reply-to THREAD_ID --body-file reply.txt
```
