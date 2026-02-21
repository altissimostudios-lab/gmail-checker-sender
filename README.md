# Gmail Checker Sender 📧

Send emails and threaded replies via Gmail API with OAuth authentication.

## Features

- ✅ **Send new emails** with full control
- ✅ **Reply to threads** (keeps conversation intact, better deliverability)
- ✅ **Custom From address** (e.g., `hello@livemoments.com.sg`)
- ✅ **CC/BCC support**
- ✅ **Save as draft** for review
- ✅ **Preview before send** (safety first!)
- ✅ **JSON output** for automation

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

## Requirements

- Python 3.7+
- Google API credentials with `gmail.modify` scope

## License

MIT
