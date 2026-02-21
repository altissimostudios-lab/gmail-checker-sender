# Gmail Checker Sender

Complete email and calendar workflow for LiveMoments business operations.

## Tools

| Tool | Purpose |
|------|---------|
| `capture_email.py` | Capture email metadata & thread ID for instant reference |
| `send_email.py` | Send emails and threaded replies |
| `add_calendar_event.py` | Add events to LiveMoments calendars (auto-routes by status) |
| `notify_designer.py` | Notify designer for Instant Print bookings |

---

## Quick Start

### 1. Setup OAuth Credentials

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

---

## LiveMoments Booking Workflow

### Step 1: Capture Inquiry

Capture email from potential client:

```bash
./capture_email.py \
  --query "from:jean@bakermckenzie.com subject:quotation" \
  --save
```

**Output:**
- Thread ID stored in `email_cache.json`
- Extract: `19c651bb21dfb4cb` for replies

### Step 2: Draft & Send Quote

Create quote and send reply (maintains thread):

```bash
./send_email.py \
  --to "jean@bakermckenzie.com" \
  --reply-to "19c651bb21dfb4cb" \
  --reply-subject "Request for quotation" \
  --body-file quote.txt \
  --from "hello@livemoments.com.sg" \
  --draft  # Review first, then send
```

### Step 3: Add to Calendar (TBC)

Add as tentative booking (Purple Administration calendar):

```bash
./add_calendar_event.py \
  --company "Baker McKenzie" \
  --poc "Jean" \
  --type EVENT \
  --date 2026-05-21 \
  --start 09:00 \
  --end 20:30 \
  --location "Conrad Singapore Marina Bay" \
  --email-id "19c651bb21dfb4cb"
```

**Result:** 🟣 Purple event in Administration calendar

### Step 4: Confirm Booking

#### For EVENT Coverage:

```bash
./add_calendar_event.py \
  --company "Baker McKenzie" \
  --poc "Jean" \
  --type EVENT \
  --date 2026-05-21 \
  --start 09:00 \
  --end 20:30 \
  --location "Conrad Singapore Marina Bay" \
  --email-id "19c651bb21dfb4cb" \
  --status CONFIRMED
```

**Result:** 🔴 Red event in Main calendar

#### For LIVE (Instant Prints):

**4a. Move calendar event to confirmed:**
```bash
./add_calendar_event.py \
  --company "HR&Sam Wedding" \
  --poc "Samantha-May" \
  --type LIVE \
  --date 2026-05-24 \
  --start 18:00 \
  --end 22:00 \
  --location "InterContinental Singapore Robertson Quay" \
  --email-id "thread_id_here" \
  --status CONFIRMED
```

**4b. Send client confirmation email** (use `send_email.py`)

**4c. Notify designer for overlay coordination:**
```bash
./notify_designer.py \
  --client "HR&Sam Wedding" \
  --poc "Samantha-May" \
  --email "samantha@email.com" \
  --date "24 May 2026" \
  --time "6:00 PM" \
  --venue "InterContinental Singapore Robertson Quay" \
  --type "Wedding"
```

**Designer receives:**
- Client POC email for direct coordination
- Event date, time, venue
- Event type
- Instructions to liaise directly for overlay design
- Alfred is auto-CC'd on all correspondence

**Result:** 🔴 Red event in Main calendar + Designer notified

---

## Visual Calendar System

| Status | Calendar | Color | Meaning |
|--------|----------|-------|---------|
| **TBC** | Administration | 🟣 Purple | Quote sent, pending confirmation. Can negotiate/move dates. |
| **CONFIRMED** | Main | 🔴 Red | Deposit received, locked in. Committed date. |

**Prevents double bookings** — see all tentative and confirmed events at a glance!

---

## Upsell Strategy

### Evening Reception Enhancement

When client has networking session (5:30PM+):

**Option A: Live Projection** — $300
- Photos showcased on screen in near real-time
- Dynamic, engaging atmosphere

**Option B: Instant Prints (3 Hours)** — $1,398
- At 5:30PM, Instant Print team seamlessly takes over from event coverage photographer
- Guests receive physical prints within 10 seconds
- Continuous photography coverage rolls on—no gaps
- **Includes FREE Live Projection**
- *(Adds only $648 to upgrade networking session)*

**Handover Logic:** Event coverage photographer ends at 5:30PM, Instant Print photographer continues coverage seamlessly.

---

## Designer Notification Workflow

**Trigger:** Instant Print booking confirmed (status = CONFIRMED + type = LIVE)

**To:** designer@livemoments.com.sg  
**From:** hello@livemoments.com.sg  
**CC:** Alfred (auto-handled by designer)

**Email Format:**
```
Subject: New Booking - [Client Name] - [Date]

Hi Ting Ting,

We have a new instant print booking confirmed.

Please liaise directly with the client for the overlay design:

Client: [POC Name]
Email: [POC email]
Event Date: [Date]
Start Time: [Time]
Venue: [Location]
Event Type: [Corporate/Wedding/etc.]

Thank you!
```

**Notes:**
- Ting Ting has worked with Alfred for 8+ years, knows the workflow
- Designer liaises directly with client for overlay design
- Alfred is CC'd on all correspondence automatically
- No package details needed (Diamond/Platinum not relevant to designer)

---

## Tool Reference

### capture_email.py

Capture email metadata for instant reference.

```bash
./capture_email.py --query "from:client@example.com" --save
```

| Flag | Description |
|------|-------------|
| `--query`, `-q` | Gmail search query (required) |
| `--save`, `-s` | Save to cache file |
| `--json`, `-j` | Output as JSON |
| `--cache-path` | Custom cache location |

### send_email.py

Send emails and replies via Gmail API.

```bash
# Send new email
./send_email.py --to "client@example.com" --subject "Quote" --body "Hello"

# Reply to thread
./send_email.py --to "client@example.com" --reply-to "THREAD_ID" \
  --reply-subject "Original Subject" --body-file reply.txt

# Save as draft
./send_email.py --to "client@example.com" --subject "Draft" --body "Content" --draft
```

| Flag | Description |
|------|-------------|
| `--to` | Recipient email (required) |
| `--subject` | Email subject |
| `--body` | Email body text |
| `--body-file` | File containing body |
| `--from` | Custom From address |
| `--cc`, `--bcc` | CC/BCC recipients |
| `--reply-to` | Thread ID to reply to |
| `--reply-subject` | Original subject for replies |
| `--draft` | Save as draft instead of sending |
| `--yes` | Auto-confirm without preview |
| `--json` | Output as JSON |

### add_calendar_event.py

Add events to LiveMoments calendars with auto-routing.

```bash
# TBC event (Purple Administration)
./add_calendar_event.py --company "Client" --poc "Name" --type EVENT \
  --date 2026-05-21 --start 09:00 --end 20:30 \
  --location "Venue" --email-id "thread_id"

# Confirmed event (Red Main)
./add_calendar_event.py --company "Client" --poc "Name" --type LIVE \
  --date 2026-05-21 --start 18:00 --end 22:00 \
  --location "Venue" --email-id "thread_id" --status CONFIRMED
```

| Flag | Description |
|------|-------------|
| `--company` | Client/company name (required) |
| `--poc` | Point of contact name (required) |
| `--type` | `EVENT` (coverage) or `LIVE` (instant prints) |
| `--date` | Event date (YYYY-MM-DD) |
| `--start`, `--end` | Time (HH:MM, 24-hour) |
| `--location` | Event venue |
| `--email-id` | Gmail thread ID for traceability |
| `--description` | Additional notes |
| `--status` | `TBC` (Purple) or `CONFIRMED` (Red) |
| `--json` | Output as JSON |

**Event Title Format:** `[TBC - ]Company - POC (TYPE)`

### notify_designer.py

Notify designer for Instant Print overlay coordination.

```bash
./notify_designer.py \
  --client "HR&Sam Wedding" \
  --poc "Samantha-May" \
  --email "samantha@email.com" \
  --date "24 May 2026" \
  --time "6:00 PM" \
  --venue "InterContinental Singapore" \
  --type "Wedding"
```

| Flag | Description |
|------|-------------|
| `--client` | Client/company name (required) |
| `--poc` | Point of contact name (required) |
| `--email` | POC email address (required) |
| `--date` | Event date (required) |
| `--time` | Start time (required) |
| `--venue` | Event venue (required) |
| `--type` | Event type: Wedding/Corporate/etc. (required) |
| `--draft` | Save as draft instead of sending |

---

## Service Rates (LiveMoments)

### Event Coverage
- Standard: $200/hr
- Premium: $250/hr
- Deliverables: Hi-res images (3800×2533px)

### Instant Print Packages

| Package | 2hrs | 3hrs | 4hrs | Add-on/hr |
|---------|------|------|------|-----------|
| **Live Diamond** | $1,715 | $2,255 | $2,688 | $500 (after 4hrs) |
| **Live Platinum** | $1,068 | $1,398 | $1,598 | $250 (after 4hrs) |

**Notes:**
- Add-on pricing applies ONLY after 4-hour mark
- 2 hours is minimum booking
- Instant Prints includes **complimentary Live Projection**

**Add-ons:**
- Additional printer: $180/hr/printer
- Live Projection: $300 (standalone) / FREE with Instant Prints
- Custom text bubbles (6pcs): $200
- Illustrated props (8pcs): $280
- Online gallery (6mo): $120
- Standard props + backdrop: $250

---

## Safety Features

1. **Preview Before Send** — Always shows email before sending (unless `--yes`)
2. **Reply Threading** — Proper In-Reply-To headers maintain conversation flow
3. **Draft Mode** — Review before committing
4. **Email ID in Calendar** — Full traceability from event to original inquiry
5. **Visual Status** — Purple (TBC) vs Red (Confirmed) prevents booking conflicts
6. **Designer Auto-Notify** — Instant Print bookings automatically notify designer

---

## Requirements

- Python 3.7+
- Google OAuth credentials with Gmail + Calendar scopes
- `gmail.readonly`, `gmail.modify`, `calendar` OAuth scopes
- Calendar IDs configured in script:
  - Main (Red): `livemomentssg@gmail.com`
  - Administration (Purple): `jml0dbb0k0pq0qfdlhdo89oql0@group.calendar.google.com`

---

## Cache File

Emails cached at:
```
~/.nanobot/workspace/skills/gmail-checker-sender/email_cache.json
```

Each entry contains: `thread_id`, `message_id`, `from`, `to`, `subject`, `body`, `date`

---

## License

MIT
