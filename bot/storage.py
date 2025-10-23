import csv
import json 
from pathlib import Path
from typing import List, Dict, Any

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Define file paths for data storage 
DROPS_FILE = PROJECT_ROOT / "drops.csv" # CSV file to store sneaker drop info 
SUBS_FILE = PROJECT_ROOT / "subscriptions.json" # JSON file to store user subscription

def load_drops() -> List[Dict[str, str]]:
    """
    Load sneaker drops from CSV file.
    Returns a list of dictionaries, each containing drop information.
    If file doesn't exist or has errors, returns empty list.
    """
    drops = []
    if DROPS_FILE.exists(): # Check if CSV file exists 
        try: 
            # Open CSV file and read all rows into a list of dictionaries 
            with open(DROPS_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f) # Creates a reader that maps each row to a dict
                drops = list(reader) # Convert reader to list of dictionaries 
            print(f"Loaded {len(drops)} drops from CSV")
        except Exception as e:
            # If anything goes wrong (file corruption, permission issues, etc.)
            print(f"Error loading drops: {e}")
    else:
        print("No drops file found, starting with empty list")
    return drops

def save_drops(drops: List[Dict[str, str]]) -> None:
    """
    Save sneaker drops to CSV file.
    Takes a list of dictionaries and writes them to CSV format.
    Creates the file if it doesn't exist.
    """
    try: 
        with open(DROPS_FILE, 'w', newline='', encoding='utf-8') as f:
            if drops: # Only write if we have data
                # Use keys from first dictionary as column headers 
                writer = csv.DictWriter(f, fieldnames=drops[0].keys())
                writer.writeheader() # Write column names as first row
                writer.writerows(drops) # Write all data rows
        print(f"Saved {len(drops)} drops to CSV")
    except Exception as e:
        print(f"Error saving drops: {e}")

def load_subs() -> List[Dict[str, Any]]:
    """
    Load user subscriptions from JSON file.
    Returns a list of subscription dictionaries.
    Each subscription tracks which drops a user wants reminders for. 
    """
    subs = []
    if SUBS_FILE.exists(): # Check if JSON file exists
        try:
            # Open JSON file and parse it into Python objects
            with open(SUBS_FILE, 'r', encoding='utf-8') as f:
                subs = json.load(f) # JSON to Python list/dict
            print(f"Loaded {len(subs)} subscriptions")
        except Exception as e:
            # Handle JSON parsing errors 
            print(f"Error loading subscriptions: {e}")
    else: 
        print("No subscriptions file found, starting with empty list")
    return subs

def save_subs(subs: List[Dict[str, Any]]) -> None: 
    """
    Save user subscriptions to JSON file.
    Takes a list of subscription dictionaries and writes them as formatted JSON
    """
    try: 
        with open(SUBS_FILE, 'w', encoding='utf-8') as f:
            # Write JSON with nice formatting 
            json.dump(subs, f, indent=2)
        print(f"Saved {len(subs)} subscriptions")
    except Exception as e:
        print(f"Error saving subscriptions: {e}")

if __name__ == '__main__':
    # This section only runs when this file is executed directly
    # Used for testing storage functions
    print("Testing storage functions...")

    # Test loading (should be empty initially since files don't exist yet)
    drops = load_drops()
    subs = load_subs()

    # Sample data to test save functions
    sample_drops = [
        {
            "drop_id": "1", # Unique identifier for drop
            "name": "Air Jordan 1 Retro High OG",  # Full name of the sneaker
            "brand": "Nike",  # Brand/manufacturer
            "drop_iso": "2024-01-15T10:00:00-05:00",  # Release date in ISO format with timezone
            "url": "https://example.com/jordan1"  # Link to more info or purchase
        }
    ]

    # Sample subscription data structure
    sample_subs = [
        {
            "drop_id": "1",  # Which drop this subscription is for
            "user": "me",  # Who is subscribed (could be Discord user ID later)
            "reminders_sent": []  # Track which reminder stages we've already sent
        }
    ]

    # Test saving sample data
    save_drops(sample_drops)
    save_subs(sample_subs)
    
    print("Storage test completed!")