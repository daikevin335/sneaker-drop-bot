from pathlib import Path
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Add parent directory to path so we can import storage
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.storage import Storage, load_drops 

TARGET_TZ = ZoneInfo("America/Toronto") 

def list_drops_text():
    """
    Load and display all available drops in user-friendly format.
    Shows drop_id, name, brand, and release date
    """
    drops = load_drops() 
    # If no drops found, inform 
    if not drops:
        return "No sneaker drops available at the moment. Run the scraper first!"
    
    # Print header 
    print(f"\n Available Drops ({len(drops)} total):\n")
    print(f"{'Drop ID':<8} {'Name':<35} {'Brand':<15} {'Release Date':<20}")
    print("-" * 110) 

    for drop in drops:
        drop_id = drop.get('drop_id', 'N/A')[:38]   # Truncate long IDs
        name = drop.get('name', 'N/A')[:33]         # Truncate long names 
        brand = drop.get('brand', 'N/A')[:13]
        release_date = drop.get('release_date', 'N/A')[:20]

        # Format date 
        try:
            dt = datetime.fromisoformat(drop_iso)
            date_str = dt.strftime("%Y-%m-%d %H:%M %Z")
        except:
            date_str = release_date  # Use raw string if parsing fails

        print(f"{drop_id:<8} {name:<35} {brand:<15} {date_str:<20}")

    print()  

def add_subscription(drop_id, user="me"):
    """
    Subscribe to a drop_id for reminder notifications.
    Creates a subscription object tracking which reminders have been sent.
    """ 
    # Load exisitng data
    drops = load_drops() 
