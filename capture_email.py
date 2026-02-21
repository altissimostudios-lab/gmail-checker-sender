#!/usr/bin/env python3
"""
Email Capture Tool - One-shot metadata extraction
Saves email details for instant reference without re-searching
"""

import os
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime

# Gmail API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Error: Google API libraries not installed")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    exit(1)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Cache file location
CACHE_FILE = Path.home() / '.nanobot' / 'workspace' / 'skills' / 'gmail-checker-sender' / 'email_cache.json'


def get_credentials():
    """Get or refresh Gmail API credentials"""
    creds = None
    token_path = Path('token.json')
    credentials_path = Path('credentials.json')
    
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                print("Error: credentials.json not found")
                print("Please download credentials from Google Cloud Console")
                exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def decode_body(payload):
    """Extract and decode email body from payload"""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType', '')
            
            if mime_type == 'text/plain' and 'data' in part.get('body', {}):
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                break
            elif mime_type == 'text/html' and 'data' in part.get('body', {}):
                # Store HTML but prefer plain text if available
                if not body:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif 'parts' in part:
                # Recursive for nested parts
                nested_body = decode_body(part)
                if nested_body:
                    body = nested_body
                    break
    elif 'data' in payload.get('body', {}):
        data = payload['body']['data']
        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    return body


def extract_headers(headers):
    """Extract key headers into a dictionary"""
    result = {}
    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        if name in ['from', 'to', 'cc', 'bcc', 'subject', 'date', 'message-id']:
            result[name] = value
    return result


def capture_email(service, query, save=False, json_output=False, cache_path=None):
    """Capture email metadata in one shot"""
    # Use provided cache path or default
    cache_file = cache_path if cache_path else CACHE_FILE
    
    # Search for emails
    results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print(f"No emails found for query: {query}")
        return None
    
    captured = []
    
    for msg_meta in messages:
        msg_id = msg_meta['id']
        thread_id = msg_meta['threadId']
        
        # Get full message details
        msg = service.users().messages().get(
            userId='me', 
            id=msg_id,
            format='full'
        ).execute()
        
        payload = msg.get('payload', {})
        headers = extract_headers(payload.get('headers', []))
        body = decode_body(payload)
        
        # Build capture object
        email_data = {
            'captured_at': datetime.now().isoformat(),
            'message_id': msg_id,
            'thread_id': thread_id,
            'from': headers.get('from', ''),
            'to': headers.get('to', ''),
            'cc': headers.get('cc', ''),
            'bcc': headers.get('bcc', ''),
            'subject': headers.get('subject', ''),
            'date': headers.get('date', ''),
            'body': body[:5000] if body else '',  # Limit body size
            'search_query': query,
            'snippet': msg.get('snippet', '')
        }
        
        captured.append(email_data)
    
    # Save to cache if requested
    if save:
        cache_data = {}
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
            except:
                cache_data = {}
        
        # Add new captures with timestamp key
        for email in captured:
            key = f"{email['thread_id']}_{email['message_id'][:8]}"
            cache_data[key] = email
        
        # Ensure directory exists
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        if not json_output:
            print(f"✓ Saved {len(captured)} email(s) to cache: {cache_file}")
    
    # Output results
    if json_output:
        print(json.dumps(captured, indent=2))
    else:
        # Pretty print summary
        for i, email in enumerate(captured, 1):
            print(f"\n{'='*60}")
            print(f"EMAIL #{i}")
            print(f"{'='*60}")
            print(f"Thread ID:  {email['thread_id']}")
            print(f"Message ID: {email['message_id']}")
            print(f"From:       {email['from']}")
            print(f"To:         {email['to']}")
            print(f"CC:         {email['cc'] or '(none)'}")
            print(f"Subject:    {email['subject']}")
            print(f"Date:       {email['date']}")
            print(f"\nBody Preview (first 500 chars):")
            print(f"{email['body'][:500]}...")
    
    return captured


def main():
    parser = argparse.ArgumentParser(
        description='Capture email metadata for instant reference',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "from:jean subject:quotation" --save
  %(prog)s --query "from:altissimostudios subject:Test" --json
  %(prog)s --query "in:inbox is:unread" --save --json
        """
    )
    
    parser.add_argument('--query', '-q', required=True,
                        help='Gmail search query (same as Gmail search bar)')
    parser.add_argument('--save', '-s', action='store_true',
                        help='Save captured emails to cache file')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output as JSON')
    parser.add_argument('--cache-path', 
                        help=f'Custom cache file path (default: {CACHE_FILE})')
    
    args = parser.parse_args()
    
    # Get credentials and build service
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    # Capture emails
    cache_path = Path(args.cache_path) if args.cache_path else None
    capture_email(service, args.query, save=args.save, json_output=args.json, cache_path=cache_path)


if __name__ == '__main__':
    main()
