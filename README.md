# Gmail Checker Sender 📧

Send emails, capture threads, and manage Gmail workflows via API with OAuth authentication.

## Tools

| Tool | Purpose |
|------|---------|
| `send_email.py` | Send emails & threaded replies |
| `capture_email.py` | Capture email metadata for instant reference |

## Features

### send_email.py
- ✅ **Send new emails** with full control
- ✅ **Reply to threads** (keeps conversation intact, better deliverability)
- ✅ **Custom From address** (e.g., `hello@livemoments.com.sg`)
- ✅ **CC/BCC support**
- ✅ **Save as draft** for review
- ✅ **Preview before send** (safety first!)
- ✅ **JSON output** for automation

### capture_email.py
- ✅ **One-shot email capture** — extract all metadata instantly
- ✅ **Thread ID storage** — save for instant replies without re-searching
- ✅ **HTML + plain text** — captures both formats
- ✅ **Local cache** — reference emails anytime without API calls

## Quick Start

### 1. Setup OAuth

Ensure Gmail OAuth credentials exist:
```bash
~/.nanobot/credentials/gmail/livemomentssg@gmail.com.token
```

### 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Send an Email

```bash
./send_email.py \
  --to "client@example.com" \
  --subject "Hello" \
  --body "Your message here" \
  --from "hello@yourdomain.com"
```

## Usage Examples

### Reply to a Thread

```bash
./send_email.py \
  --to "client@example.com" \
  --reply-to "THREAD_ID_FROM_GMAIL" \
  --reply-subject "Original Subject" \
  --body-file reply.txt \
  --from "hello@livemoments.com.sg" \
  --cc "team@livemoments.com.sg"
```

### Save as Draft

```bash
./send_email.py \
  --to "important@client.com" \
  --subject "Quote" \
  --body-file quote.txt \
  --draft
```

### Auto-Confirm (Automation)

```bash
./send_email.py \
  --to "client@example.com" \
  --subject "Confirmation" \
  --body "Confirmed!" \
  --yes \
  --json
```

## CLI Options

| Flag | Description |
|------|-------------|
| `--to` | Recipient email (required) |
| `--subject` | Email subject (required for new emails) |
| `--body` | Email body text |
| `--body-file` | File containing email body |
| `--from` | Custom From address |
| `--cc` | CC recipients (comma-separated) |
| `--bcc` | BCC recipients (comma-separated) |
| `--reply-to` | Thread ID to reply to |
| `--reply-subject` | Original subject (for replies) |
| `--draft` | Save as draft instead of sending |
| `--yes` | Auto-confirm without preview |
| `--json` | Output as JSON |
| `--account` | Gmail account to use |

## Safety Features

1. **Preview Before Send** - Always shows email before sending (unless `--yes`)
2. **Reply Threading** - Proper In-Reply-To and References headers
3. **Custom From Verification** - Works with Gmail send-as aliases
4. **Draft Mode** - Review before committing

## Getting Thread ID

In Gmail, open the email and look at the URL:
```
https://mail.google.com/mail/u/0/#inbox/THREAD_ID_HERE
```

Copy the thread ID and use with `--reply-to`.

## Capture Email Examples

### Basic Search & Capture

```bash
./capture_email.py --query "from:client@example.com subject:quote" --save
```

### Save with JSON Output

```bash
./capture_email.py \
  --query "from:Jean.Montecillo-Romero@bakermckenzie.com" \
  --save \
  --json
```

### Get Thread ID for Reply

```bash
# Capture and save
capture_email.py --query "subject:wedding date:2026" --save

# Extract thread_id from cache
cat email_cache.json | jq '.[].thread_id'
```

### Capture Multiple Results

```bash
./capture_email.py --query "in:inbox is:unread from:important@client.com" --save
```

## Workflow: Capture → Reply

```bash
# Step 1: Capture email metadata
./capture_email.py \
  --query "from:client@example.com subject:quotation" \
  --save \
  --json

# Step 2: Use thread_id to reply (prevents spam filtering!)
./send_email.py \
  --to "client@example.com" \
  --reply-to "THREAD_ID_FROM_CAPTURE" \
  --reply-subject "Re: quotation" \
  --body-file reply.txt \
  --from "hello@yourdomain.com" \
  --yes
```

## Cache File

Emails are saved to:
```
email_cache.json
```

Each entry contains:
- `message_id` — Unique message identifier
- `thread_id` — For threaded replies ✅
- `from`, `to`, `cc` — Address fields
- `subject`, `date` — Metadata
- `body` — Full content (HTML + plain text)
- `captured_at` — Timestamp

## Requirements

- Python 3.7+
- Google API credentials
  - `send_email.py`: `gmail.modify` scope
  - `capture_email.py`: `gmail.readonly` scope

## License

MIT
