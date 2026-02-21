#!/usr/bin/env python3
"""
Add Calendar Event for LiveMoments
Auto-routes TBC events to Administration calendar, confirmed to Main calendar
"""

import os
import sys
import json
import pickle
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Calendar IDs
CALENDAR_ADMIN = "jml0dbb0k0pq0qfdlhdo89oql0@group.calendar.google.com"  # Purple - TBC events
CALENDAR_MAIN = "livemomentssg@gmail.com"  # Default - Confirmed events

DEFAULT_ACCOUNT = "livemomentssg@gmail.com"


def get_credentials_path(account):
    """Get path to OAuth token for account"""
    base_path = Path.home() / ".nanobot" / "credentials" / "gmail"
    token_file = base_path / f"{account.replace('@', '_at_')}.token"
    return token_file if token_file.exists() else None


def load_credentials(account):
    """Load OAuth credentials for Google account"""
    creds_path = get_credentials_path(account)
    
    if not creds_path:
        print(f"Error: No credentials found for {account}")
        print(f"Expected: {creds_path}")
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
        print(f"Error loading credentials: {e}")
        return None


def add_event(account, company, poc, event_type, date, start_time, end_time,
              location, email_id, description=None, status="TBC"):
    """Add event to appropriate calendar based on status"""
    
    creds = load_credentials(account)
    if not creds:
        return {'success': False, 'error': 'No credentials found'}
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Determine calendar based on status
        if status.upper() == "TBC":
            calendar_id = CALENDAR_ADMIN
            color_id = "3"  # Purple
            title_prefix = "TBC - "
        else:
            calendar_id = CALENDAR_MAIN
            color_id = None  # Default
            title_prefix = ""
        
        # Format title: [TBC - ]Company - POC (TYPE)
        title = f"{title_prefix}{company} - { POC} ({event_type.upper()})"
        
        # Build description
        desc_parts = []
        if email_id:
            desc_parts.append(f"Email ID: {email_id}")
        if description:
            desc_parts.append(description)
        desc_parts.append(f"Status: {status}")
        desc_parts.append(f"POC: {poc}")
        
        full_description = "\n\n".join(desc_parts)
        
        # Parse date and times
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_hour, start_min = map(int, start_time.split(":"))
        end_hour, end_min = map(int, end_time.split(":"))
        
        start_dt = date_obj.replace(hour=start_hour, minute=start_min)
        end_dt = date_obj.replace(hour=end_hour, minute=end_min)
        
        # Create event body
        event_body = {
            'summary': title,
            'location': location,
            'description': full_description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Singapore'
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Singapore'
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 7 * 24 * 60},  # 1 week
                    {'method': 'email', 'minutes': 3 * 24 * 60},  # 3 days
                ]
            }
        }
        
        if color_id:
            event_body['colorId'] = color_id
        
        # Create event
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        
        return {
            'success': True,
            'event_id': event.get('id'),
            'calendar_id': calendar_id,
            'title': title,
            'html_link': event.get('htmlLink'),
            'status': status
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(
        description='Add LiveMoments events to calendar (auto-routes by status)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # TBC event (goes to Purple Administration calendar)
  %(prog)s --company "Baker McKenzie" --poc "Jean" --type EVENT \\
    --date 2026-05-21 --start 09:00 --end 20:30 \\
    --location "Conrad Singapore" --email-id "abc123"

  # Confirmed event (goes to Main calendar)
  %(prog)s --company "Wedding" --poc "Sarah" --type LIVE \\
    --date 2026-07-15 --start 18:00 --end 22:00 \\
    --location "Hotel" --email-id "xyz789" --status CONFIRMED
        """
    )
    
    parser.add_argument('--account', default=DEFAULT_ACCOUNT,
                        help='Google account to use')
    parser.add_argument('--company', required=True,
                        help='Company/client name')
    parser.add_argument('--poc', required=True,
                        help='Point of contact name')
    parser.add_argument('--type', required=True, choices=['EVENT', 'LIVE'],
                        help='EVENT=event coverage, LIVE=instant prints')
    parser.add_argument('--date', required=True,
                        help='Event date (YYYY-MM-DD)')
    parser.add_argument('--start', required=True,
                        help='Start time (HH:MM, 24-hour)')
    parser.add_argument('--end', required=True,
                        help='End time (HH:MM, 24-hour)')
    parser.add_argument('--location', required=True,
                        help='Event venue/location')
    parser.add_argument('--email-id', required=True,
                        help='Gmail thread/message ID for traceability')
    parser.add_argument('--description',
                        help='Additional notes')
    parser.add_argument('--status', default='TBC', choices=['TBC', 'CONFIRMED'],
                        help='TBC=Purple Admin calendar, CONFIRMED=Main calendar')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    
    args = parser.parse_args()
    
    result = add_event(
        args.account,
        args.company,
        args.poc,
        args.type,
        args.date,
        args.start,
        args.end,
        args.location,
        args.email_id,
        args.description,
        args.status
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get('success'):
            status_emoji = "🟣" if result['status'] == 'TBC' else "🔵"
            print(f"{status_emoji} Event created successfully!")
            print(f"   Title: {result['title']}")
            print(f"   Calendar: {'Administration (Purple)' if result['status'] == 'TBC' else 'Main'}")
            print(f"   Link: {result['html_link']}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
