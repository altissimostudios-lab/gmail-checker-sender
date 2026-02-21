#!/usr/bin/env python3
"""
Notify Designer - Send Instant Print booking notification to designer
Part of gmail-checker-sender skill

Notifies Ting Ting (designer@livemoments.com.sg) when an Instant Print
booking is confirmed, so she can coordinate overlay design directly with client.
"""

import os
import sys
import json
import pickle
import base64
import argparse
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Activate virtual environment if running directly
venv_path = Path(__file__).parent / "venv"
if venv_path.exists():
    site_packages = list(venv_path.glob("lib/python*/site-packages"))
    if site_packages:
        sys.path.insert(0, str(site_packages[0]))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DEFAULT_ACCOUNT = "livemomentssg@gmail.com"
DESIGNER_EMAIL = "designer@livemoments.com.sg"
FROM_ADDRESS = "hello@livemoments.com.sg"


def get_credentials_path(account):
    """Get path to OAuth token for account"""
    base_path = Path.home() / ".nanobot" / "credentials" / "gmail"
    token_file = base_path / f"{account.replace('@', '_at_')}.token"
    
    if not token_file.exists():
        alt_path = Path.home() / ".nanobot" / "credentials" / f"{account}.json"
        if alt_path.exists():
            return alt_path
    
    return token_file if token_file.exists() else None


def load_credentials(account):
    """Load OAuth credentials for Gmail account"""
    creds_path = get_credentials_path(account)
    
    if not creds_path:
        return None
    
    try:
        with open(creds_path, 'rb') as token:
            creds = pickle.load(token)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(creds_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    except Exception as e:
        print(f"Error loading credentials for {account}: {e}", file=sys.stderr)
        return None


def build_designer_email(client, poc, poc_email, date, time, venue, event_type):
    """Build the designer notification email body"""
    
    subject = f"New Booking - {client} - {date}"
    
    body = f"""Hi Ting Ting,

We have a new instant print booking confirmed.

Please liaise directly with the client for the overlay design:

Client: {poc}
Email: {poc_email}
Event Date: {date}
Start Time: {time}
Venue: {venue}
Event Type: {event_type}

Thank you!"""
    
    return subject, body


def preview_email(to, subject, body, sender):
    """Display email preview for confirmation"""
    print("\n" + "="*70)
    print("📧 DESIGNER NOTIFICATION PREVIEW")
    print("="*70)
    print(f"From: {sender}")
    print(f"To: {to}")
    print(f"Subject: {subject}")
    print("-"*70)
    print(body)
    print("="*70)
    print()


def send_designer_notification(account, client, poc, poc_email, date, time, 
                                venue, event_type, auto_confirm=False, 
                                draft=False):
    """Send notification to designer for Instant Print booking"""
    
    creds = load_credentials(account)
    if not creds:
        return {
            'success': False,
            'error': f'No credentials found for {account}. Run OAuth setup first.'
        }
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Build email content
        subject, body = build_designer_email(client, poc, poc_email, date, 
                                              time, venue, event_type)
        
        # Show preview
        if not auto_confirm:
            preview_email(DESIGNER_EMAIL, subject, body, FROM_ADDRESS)
            
            action = "Save as draft" if draft else "Send"
            response = input(f"{action} this notification? (yes/no): ").strip().lower()
            if response not in ['yes', 'y', 'send', 'draft']:
                return {
                    'success': False,
                    'error': 'User cancelled',
                    'preview_only': True
                }
        
        # Create MIME message
        message = MIMEMultipart('alternative')
        message['to'] = DESIGNER_EMAIL
        message['from'] = FROM_ADDRESS
        message['subject'] = subject
        
        # Add body as HTML and plain text
        plain_text = body
        html_body = body.replace('\n', '<br>')
        
        msg_plain = MIMEText(plain_text, 'plain')
        msg_html = MIMEText(html_body, 'html')
        
        message.attach(msg_plain)
        message.attach(msg_html)
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        msg_body = {'raw': raw}
        
        if draft:
            saved = service.users().drafts().create(userId='me', body={'message': msg_body}).execute()
            return {
                'success': True,
                'draft_id': saved.get('id'),
                'sender': FROM_ADDRESS,
                'to': DESIGNER_EMAIL,
                'subject': subject,
                'is_draft': True,
                'client': client,
                'poc': poc
            }
        else:
            sent = service.users().messages().send(userId='me', body=msg_body).execute()
            
            return {
                'success': True,
                'message_id': sent.get('id'),
                'thread_id': sent.get('threadId'),
                'sender': FROM_ADDRESS,
                'to': DESIGNER_EMAIL,
                'subject': subject,
                'client': client,
                'poc': poc
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Notify designer for Instant Print booking'
    )
    parser.add_argument('--account', default=DEFAULT_ACCOUNT, 
                        help='Gmail account to use')
    parser.add_argument('--client', required=True, 
                        help='Client/company name')
    parser.add_argument('--poc', required=True, 
                        help='Point of contact name')
    parser.add_argument('--email', required=True, 
                        help='POC email address')
    parser.add_argument('--date', required=True, 
                        help='Event date (e.g., "24 May 2026")')
    parser.add_argument('--time', required=True, 
                        help='Start time (e.g., "6:00 PM")')
    parser.add_argument('--venue', required=True, 
                        help='Event venue')
    parser.add_argument('--type', required=True, 
                        help='Event type (Wedding/Corporate/etc.)')
    parser.add_argument('--draft', action='store_true', 
                        help='Save as draft instead of sending')
    parser.add_argument('--yes', action='store_true', 
                        help='Auto-confirm without preview')
    parser.add_argument('--json', action='store_true', 
                        help='Output as JSON')
    
    args = parser.parse_args()
    
    # Send notification
    result = send_designer_notification(
        args.account,
        args.client,
        args.poc,
        args.email,
        args.date,
        args.time,
        args.venue,
        args.type,
        auto_confirm=args.yes,
        draft=args.draft
    )
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get('success'):
            if result.get('is_draft'):
                print(f"✅ Designer notification saved as draft!")
                print(f"   Draft ID: {result.get('draft_id')}")
            else:
                print(f"✅ Designer notification sent successfully!")
                print(f"   Message ID: {result.get('message_id')}")
            print(f"   Designer: {result.get('to')}")
            print(f"   Client: {result.get('client')} ({result.get('poc')})")
            print(f"   Subject: {result.get('subject')}")
        elif result.get('preview_only'):
            print("📋 Preview shown. Notification not sent.")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
