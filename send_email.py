#!/usr/bin/env python3
"""
Gmail Sender - Send emails and replies via Gmail API
Part of gmail-checker-sender skill

Features:
- Send new emails
- Reply to threads (keeps conversation intact)
- Custom From address support
- CC/BCC
- Save as draft
- Preview before send (safety)
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


def preview_email(to, subject, body, cc=None, bcc=None, sender=None):
    """Display email preview for confirmation"""
    print("\n" + "="*70)
    print("📧 EMAIL PREVIEW")
    print("="*70)
    if sender:
        print(f"From: {sender}")
    print(f"To: {to}")
    if cc:
        print(f"Cc: {cc}")
    if bcc:
        print(f"Bcc: {bcc}")
    print(f"Subject: {subject}")
    print("-"*70)
    print(body)
    print("="*70)
    print()


def send_email(account, to, subject, body, cc=None, bcc=None, auto_confirm=False,
               from_address=None, draft=False, thread_id=None):
    """Send email using Gmail API"""
    
    creds = load_credentials(account)
    if not creds:
        return {
            'success': False,
            'error': f'No credentials found for {account}. Run OAuth setup first.'
        }
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get sender email (use override if provided)
        if from_address:
            sender = from_address
        else:
            profile = service.users().getProfile(userId='me').execute()
            sender = profile.get('emailAddress', account)
        
        # Show preview
        if not auto_confirm:
            preview_email(to, subject, body, cc, bcc, sender)
            
            action = "Save as draft" if draft else "Send"
            response = input(f"{action} this email? (yes/no): ").strip().lower()
            if response not in ['yes', 'y', 'send', 'draft']:
                return {
                    'success': False,
                    'error': 'User cancelled',
                    'preview_only': True
                }
        
        # Create MIME message
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        # Add body as HTML and plain text
        plain_text = body
        html_body = body.replace('\n', '<br>')
        
        msg_plain = MIMEText(plain_text, 'plain')
        msg_html = MIMEText(html_body, 'html')
        
        message.attach(msg_plain)
        message.attach(msg_html)
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        msg_body = {'raw': raw}
        
        if thread_id:
            msg_body['threadId'] = thread_id
        
        if draft:
            saved = service.users().drafts().create(userId='me', body={'message': msg_body}).execute()
            return {
                'success': True,
                'draft_id': saved.get('id'),
                'sender': sender,
                'to': to,
                'subject': subject,
                'is_draft': True
            }
        else:
            sent = service.users().messages().send(userId='me', body=msg_body).execute()
            
            return {
                'success': True,
                'message_id': sent.get('id'),
                'thread_id': sent.get('threadId'),
                'sender': sender,
                'to': to,
                'subject': subject
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_reply(account, thread_id, to, subject, body, cc=None, auto_confirm=False,
               from_address=None, draft=False):
    """Send a reply to an existing thread"""
    
    creds = load_credentials(account)
    if not creds:
        return {
            'success': False,
            'error': f'No credentials found for {account}'
        }
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get sender email
        if from_address:
            sender = from_address
        else:
            profile = service.users().getProfile(userId='me').execute()
            sender = profile.get('emailAddress', account)
        
        # Get thread to set references
        thread = service.users().threads().get(userId='me', id=thread_id).execute()
        original_msg_id = thread['messages'][-1]['id']
        
        # Create message with thread reference
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = f"Re: {subject.replace('Re: ', '')}"
        message['In-Reply-To'] = original_msg_id
        message['References'] = original_msg_id
        
        if cc:
            message['cc'] = cc
        
        plain_text = body
        html_body = body.replace('\n', '<br>')
        
        msg_plain = MIMEText(plain_text, 'plain')
        msg_html = MIMEText(html_body, 'html')
        
        message.attach(msg_plain)
        message.attach(msg_html)
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        if not auto_confirm:
            preview_email(to, subject, body, cc, None, sender)
            action = "Save as draft" if draft else "Send"
            response = input(f"{action} this reply? (yes/no): ").strip().lower()
            if response not in ['yes', 'y', 'send', 'draft']:
                return {
                    'success': False,
                    'error': 'User cancelled',
                    'preview_only': True
                }
        
        if draft:
            draft_body = {'message': {'raw': raw, 'threadId': thread_id}}
            saved = service.users().drafts().create(userId='me', body=draft_body).execute()
            return {
                'success': True,
                'draft_id': saved.get('id'),
                'thread_id': thread_id,
                'sender': sender,
                'to': to,
                'subject': subject,
                'is_draft': True
            }
        else:
            sent = service.users().messages().send(
                userId='me',
                body={'raw': raw, 'threadId': thread_id}
            ).execute()
            
            return {
                'success': True,
                'message_id': sent.get('id'),
                'thread_id': sent.get('threadId'),
                'sender': sender,
                'to': to,
                'subject': subject
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(description='Send emails via Gmail API')
    parser.add_argument('--account', default=DEFAULT_ACCOUNT, help='Gmail account to use')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', help='Email body (or use --body-file)')
    parser.add_argument('--body-file', help='File containing email body')
    parser.add_argument('--cc', help='CC recipients (comma-separated)')
    parser.add_argument('--bcc', help='BCC recipients (comma-separated)')
    parser.add_argument('--from', dest='from_address', help='From address override')
    parser.add_argument('--reply-to', help='Thread ID to reply to')
    parser.add_argument('--reply-subject', help='Original subject (for replies)')
    parser.add_argument('--draft', action='store_true', help='Save as draft instead of sending')
    parser.add_argument('--yes', action='store_true', help='Auto-confirm without preview')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Get body content
    if args.body_file:
        with open(args.body_file, 'r') as f:
            body = f.read()
    elif args.body:
        body = args.body
    else:
        print("Enter email body (Ctrl+D to finish):")
        body = sys.stdin.read()
    
    # Send email or reply
    if args.reply_to:
        if not args.reply_subject:
            print("Error: --reply-subject required when using --reply-to")
            sys.exit(1)
        result = send_reply(
            args.account,
            args.reply_to,
            args.to,
            args.reply_subject,
            body,
            cc=args.cc,
            auto_confirm=args.yes,
            from_address=args.from_address,
            draft=args.draft
        )
    else:
        result = send_email(
            args.account,
            args.to,
            args.subject,
            body,
            cc=args.cc,
            bcc=args.bcc,
            auto_confirm=args.yes,
            from_address=args.from_address,
            draft=args.draft,
            thread_id=args.reply_to
        )
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get('success'):
            if result.get('is_draft'):
                print(f"✅ Draft saved successfully!")
                print(f"   Draft ID: {result.get('draft_id')}")
            else:
                print(f"✅ Email sent successfully!")
                print(f"   Message ID: {result.get('message_id')}")
            print(f"   From: {result.get('sender')}")
            print(f"   To: {result.get('to')}")
            print(f"   Subject: {result.get('subject')}")
        elif result.get('preview_only'):
            print("📋 Preview shown. Email not saved/sent.")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
