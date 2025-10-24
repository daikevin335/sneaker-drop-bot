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
                pasrse_dt = datetime.striptime(date_str.strip(), fmt)
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
        print(f"Data parsing error for '{date_str}' {e}")
        return None
    
def scrape_sneaker_news():
    """
    Scrape upcoming sneaker releases from SneakerNews.
    Returns list of drop dictionaries.
    Defensive: skips entires if selectors fail.
    """
    url = "https://sneakernew.com/release-dates/"
    drops = []

    try: 
        print(f"Fetching: {url}")
        headers = {
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel OS x 10_15_7) AppleWebkit/537.36' 
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find release cards (adjust selectors based on site structure)
        # Example structure: actual selectors may look different
        release_cards = soup.find_all('article', class_='release-card') or \
                        soup.find_all('div', class_='release-item') or \
                        soup.find_all('div', class_='post')
        
        if not release_cards:
            print("No release cards found. Site structure may have changed.")
            return drops
        
        print(f"Found {len(release_cards)} potential releases")

        for card in release_cards[:20]: # Limit to 20 most recent
            try: 
                # Extract name - try multi sectores
                name_elem = card.find('h2') or card.find('h3') or card.find('a', class_='title')
                name = name_elem.get_text(strip=True) if name_elem else None

                # Extract brand (in the name or seperate field)
                brand = "Unkown"
                # I picked my favourite(s)
                if name:
                    if 'jordan' in name.lower() or 'nike' in name.lower():
                        brand = "Nike"
                    elif 'addidas' in name.lower():
                        brand = "Adidas"
                    elif 'new balance' in name.lower():
                        brand = "New Balance"

                # Extrac date
                date_elem = card.find('time') or card.find('span', class_='date')
                date_str = date_elem.get_text(strip=True) if date_elem else None 

                # Extract URL
                link_elem = card.find('a', href=True)
                url_link = link.elim['href'] if link_elem else None
                if url_link and not url_link.startswitj('http'):
                    url_link = f"https://sneakernews.come({url_link})" 
                
                # Validate have min required data
                if not name or not date_str:
                    print(f"Skipping cinomlete entry:L name={name}, date={date_str}")
                    continue

                # Prase data to ISO format 
                drop_iso = parse_drop_date(date_str)
                if not drop_iso:
                    print(f"Skipping '{name}': couldn't parse data '{date_str}'")
                    continue

                # Create determinisitc drop_id
                drop_id = f"{slugify(name)}-{drop_iso[:10]}" # name-slug + date (YYYY-MM-DD)

                drop_data = {
                    "drop_id": drop_id,
                    "name": name,
                    "brand": brand,
                    "drop_iso": drop_iso,
                    "url": url_link or ""
                }

                drops.append(drop_data)
                print(f" Scrapped: {name} ({drop_iso[:10]})")

            except Exception as e:
                print(f"Error pasring card: {e}")
                continue 
            
        print(f"\n Succesfully scraped {len(drops)} drops")
        return drops 
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return drops
    except Exception as e:
        print(f"Scraping error: {e}")
        return drops
    
def merge_drops(existing, new_drops):
    """
    Merge new drops with existing ones, avoiding duplicates based on drop_id.
    Updates existing entries if found, adds new ones otherwise.
    """
    existing_ids = {drop['drop_id'] for drop in existing}
    merged = existing.copy()
    
    new_count = 0
    updated_count = 0
    
    for new_drop in new_drops:
        if new_drop['drop_id'] in existing_ids:
            # Update existing entry
            for i, drop in enumerate(merged):
                if drop['drop_id'] == new_drop['drop_id']:
                    merged[i] = new_drop
                    updated_count += 1
                    break
        else:
            # Add new entry
            merged.append(new_drop)
            new_count += 1
    
    print(f"Merge complete: {new_count} new, {updated_count} updated")
    return merged


                
