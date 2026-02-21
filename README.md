# Gmail Checker Sender 📧

Complete email and calendar workflow automation for LiveMoments business operations.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **📨 Email Capture** — Extract thread IDs and metadata instantly
- **📤 Send & Reply** — Send emails and threaded replies via Gmail API
- **📅 Calendar Integration** — Auto-route TBC events to Administration (Purple), confirmed to Main (Blue)
- **🔒 OAuth Authentication** — Secure, no password storage
- **🎨 Visual Booking System** — Purple=TBC, Blue=Confirmed (prevents double bookings!)

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/altissimostudios-lab/gmail-checker-sender.git
cd gmail-checker-sender
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Setup OAuth credentials
# Place your Google OAuth token at:
~/.nanobot/credentials/gmail/livemomentssg@gmail.com.token

# 3. Capture an email
./capture_email.py --query "from:client@example.com subject:quote" --save

# 4. Send a reply
./send_email.py --to "client@example.com" --reply-to "THREAD_ID" \
  --reply-subject "Re: Quote" --body-file response.txt

# 5. Add to calendar (TBC = Purple Administration)
./add_calendar_event.py --company "Client" --poc "Name" --type EVENT \
  --date 2026-05-21 --start 09:00 --end 20:30 \
  --location "Venue" --email-id "THREAD_ID"
```

## 📁 Tools

| Tool | Purpose | Key Features |
|------|---------|--------------|
| `capture_email.py` | Email metadata extraction | Thread ID capture, HTML+plain text, local cache |
| `send_email.py` | Email sending & replies | Threaded replies, drafts, custom From, CC/BCC |
| `add_calendar_event.py` | Calendar management | Auto-routing by status, visual color coding |

## 📋 LiveMoments Booking Workflow

```
├── 1. CAPTURE inquiry (get thread_id)
├── 2. DRAFT & SEND quote (reply to thread)
├── 3. ADD to calendar as TBC (🟣 Purple)
└── 4. UPDATE to CONFIRMED when deposited (🔵 Blue)
```

### Visual Calendar System

| Status | Calendar | Color | Purpose |
|--------|----------|-------|---------|
| **TBC** | Administration | 🟣 Purple | Quote sent, pending confirmation |
| **CONFIRMED** | Main | 🔵 Blue | Deposit received, locked in |

This prevents double bookings — you can see all tentative and confirmed events at a glance!

## 📝 Usage Examples

### Capture Email

```bash
# Basic capture
./capture_email.py --query "from:jean@company.com" --save

# With JSON output
./capture_email.py --query "subject:wedding" --save --json

# Get thread ID for reply
./capture_email.py --query "from:client@example.com" --save
cat email_cache.json | jq '.[].thread_id'
```

### Send Email

```bash
# New email
./send_email.py --to "client@example.com" \
  --subject "Quote Confirmation" \
  --body "Your quote is ready..." \
  --from "hello@livemoments.com.sg"

# Reply to thread (maintains conversation)
./send_email.py --to "client@example.com" \
  --reply-to "19c651bb21dfb4cb" \
  --reply-subject "Re: Quote Request" \
  --body-file reply.txt

# Save as draft for review
./send_email.py --to "client@example.com" \
  --subject "Draft Quote" \
  --body-file draft.txt \
  --draft

# Auto-confirm (automation mode)
./send_email.py --to "client@example.com" \
  --subject "Confirmation" --body "Confirmed!" \
  --yes --json
```

### Add Calendar Event

```bash
# TBC event (goes to Purple Administration calendar)
./add_calendar_event.py \
  --company "Baker McKenzie" \
  --poc "Jean" \
  --type EVENT \
  --date 2026-05-21 \
  --start 09:00 \
  --end 20:30 \
  --location "Conrad Singapore Marina Bay" \
  --email-id "19c651bb21dfb4cb"

# Confirmed event (goes to Blue Main calendar)
./add_calendar_event.py \
  --company "Wedding Client" \
  --poc "Sarah" \
  --type LIVE \
  --date 2026-07-15 \
  --start 18:00 \
  --end 22:00 \
  --location "Hotel Venue" \
  --email-id "xyz789" \
  --status CONFIRMED
```

## 📝 CLI Reference

### capture_email.py

| Flag | Description |
|------|-------------|
| `--query`, `-q` | Gmail search query (required) |
| `--save`, `-s` | Save to cache file |
| `--json`, `-j` | Output as JSON |

### send_email.py

| Flag | Description |
|------|-------------|
| `--to` | Recipient email (required) |
| `--subject` | Email subject |
| `--body` / `--body-file` | Email content |
| `--from` | Custom From address |
| `--cc`, `--bcc` | Carbon copy |
| `--reply-to` | Thread ID for replies |
| `--draft` | Save as draft |
| `--yes` | Auto-confirm |
| `--json` | JSON output |

### add_calendar_event.py

| Flag | Description |
|------|-------------|
| `--company` | Client/company name |
| `--poc` | Point of contact |
| `--type` | `EVENT` or `LIVE` |
| `--date` | Date (YYYY-MM-DD) |
| `--start`, `--end` | Time (HH:MM) |
| `--location` | Venue |
| `--email-id` | Thread ID for traceability |
| `--status` | `TBC` or `CONFIRMED` |

## 🛡️ Safety Features

- ✅ **Preview Before Send** — Review emails before sending
- ✅ **Reply Threading** — Maintains conversation flow
- ✅ **Draft Mode** — Save for review first
- ✅ **Email ID Tracking** — Full traceability in calendar events
- ✅ **Visual Status Colors** — Purple vs Blue prevents conflicts

## 📜 Requirements

- Python 3.7+
- Google OAuth credentials
- Gmail + Calendar API access
- OAuth scopes: `gmail.readonly`, `gmail.modify`, `calendar`

## 🔧 Setup

1. **Enable APIs** in [Google Cloud Console](https://console.cloud.google.com/)
   - Gmail API
   - Google Calendar API

2. **Create OAuth credentials** (Desktop application type)

3. **Download token** and place at:
   ```
   ~/.nanobot/credentials/gmail/livemomentssg@gmail.com.token
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📈 LiveMoments Service Rates

| Service | Rate | Notes |
|---------|------|-------|
| Event Coverage | $200-250/hr | Hi-res images (3800×2533px) |
| Live Diamond | From $1,715 | 2 photographers, 2 printers |
| Live Platinum | From $1,068 | 1 photographer, 1 printer |
| Live Projection | $300 | Included free with Instant Prints! |

## 📝 License

MIT © 2026 LiveMoments
