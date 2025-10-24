import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import re
from pathlib import Path
import sys

# Add parent directory to path to be able to import storagee
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.storage import load_drops, save_drops

# Target timezone for all drops
TARGET_TZ = ZoneInfo("America/Toronto")

def slugify(text):
    """
    Convert text to a URL-friendly slug (lowercase, spaces to dashes, alphanumerica only).
    Used to create consistentd drop IDs.
    """
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]','', text) # Remove speical chars
    text = re.sub(r'[-\s]+', '-', text)   # Replace spaces/dashes with single dash
    return text 

def parse_drop_date(date_str):
    """
    Parse various date formats and convert to ISO string in America/Toronto timezone
    Returns ISO format string or None if parsing fails.
    """
    try: # Try common formats (adjust based on actual site formats)
        formats = [
            "%B %d, %Y",           # "January 15, 2025"
            "%b %d, %Y",           # "Jan 15, 2025"
            "%Y-%m-%d",            # "2025-01-15"
            "%m/%d/%Y",            # "01/15/2025"
            "%B %d, %Y %I:%M %p", # "January 15, 2025 10:00 AM"
        ]

        pasrse_dt = None
        for fmt in formats:
            try:
                pasrse_dt = datetime.striptime(data_str.strip(), fmt)
                break
            except ValueError:
                continue

        if pasrse_dt:
            # If no time specified, default to 10:00AM
            if pasrse_dt.hour == 0 and pasrse_dt.minute == 0:
                pasrse_dt = pasrse_dt.replace(hour=10, minute=0)

            # Localize to target timezone
            localized = pasrse_dt.replace(tzinfo=TARGET_TZ)
            return localized.isoformat()
        
        return None
    except Exception as e:
        print(f"Data parsing error for '{data_str}' {e}")
        return None
    
    
