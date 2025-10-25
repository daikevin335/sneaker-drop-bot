from pathlib import Path
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Add parent directory to path so we can import storage
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.storage import load_drops, save_drops, load_subs, save_subs

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
        drop_iso = drop.get('release_date', 'N/A')[:20]

        # Format date 
        try:
            dt = datetime.fromisoformat(drop_iso)
            date_str = dt.strftime("%b %d, %Y %I:%M %p")
        except:
            date_str = drop_iso[:20] if drop_iso != 'N/A' else 'N/A' # Use raw string if parsing fails

        print(f"{drop_id:<8} {name:<35} {brand:<15} {date_str:<20}")

    print()  

def add_subscription(drop_id, user="me"):
    """
    Subscribe to a drop_id for reminder notifications.
    Creates a subscription object tracking which reminders have been sent.
    """ 
    # Load existing data
    drops = load_drops()
    subs = load_subs()

    # Validate that drop_id exists
    drop_exists = any(drop['drop_id'] == drop_id for drop in drops)
    if not drop_exists:
        print(f"\n Error: Drop ID '{drop_id}' not found. Please check available drops.\n")
        print("Run list_drops_text() to see valid drop IDs.\n")
        return False
    
    # Check if already subscribed
    for sub in subs:
        if sub['drop_id'] == drop_id and sub['user'] == user:
            print(f"\n You are already subscribed to drop ID '{drop_id}'.\n")
            return False
        
    # Create new subscription
    new_sub = {
        "drop_id": drop_id,
        "user": user,
        "reminders_sent": {
            "30": False,  # 30 minutes before
            "15": False,  # 15 minutes before
            "5": False    # 5 minutes before
        }
    }
    
    subs.append(new_sub)
    # Get drop details for confirmation
    drop_name = next((d['name'] for d in drops if d['drop_id'] == drop_id), drop_id)
    
    print(f"\n Subscribed to: {drop_name}")
    print(f"   Drop ID: {drop_id}")
    print(f"   You'll receive reminders at: T-30min, T-15min, T-5min\n")
    return True

def list_subs_text():
    """
    Display all current subscriptions with their reminder status.
    Shows which reminders have been sent for each drop.
    """
    subs = load_subs()
    drops =load_drops()

    # if not subscriptions found, inform 
    if not subs:
        print("\n No current subscriptions found.\n")
        print("Use add_subscription(drop_id) to subscribe to a drop.\n")
        return 
    
    # Create lookup for drop details 
    drops_dict = {drop['drop_id']: drop for drop in drops}

    print(f"Your subscriptions ({len(subs)} total):\n")

    # Print header
    for i, sub in enumerate(subs,1):
        drop_id = sub.get('drop_id', 'N/A')
        user = sub.get('user', 'N/A')
        reminders = sub.get('reminders_sent', {})   

        # Get drop details if available
        drop = drops_dict.get(drop_id)
        if drop:
            name = drop.get('name', drop_id)[:30]  
            drop_iso = drop.get('drop_iso', 'N/A')[:20] 
            try:
                dt = datetime.fromisoformat(drop_iso)
                date_str = dt.strftime("%b %d, %Y %I:%M %p")
            except:
                date_str = drop_iso 
    
        else: 
            name = drop_id
            date_str = 'N/A'
            
        print(f"{i}. {name}")
        print(f"   Drop ID: {drop_id}")
        print(f"   Release Date: {date_str}")
        print(f"   User: {user}")

        # Show reminder status
        sent_30 = "Checked" if reminders.get("30") else "Pending"
        sent_15 = "Checked" if reminders.get("15") else "Pending"
        sent_5 = "Checked" if reminders.get("5") else "Pending"

        print(f"   Reminders Sent: [T-30min: {sent_30}] [T-15min: {sent_15}] [T-5min: {sent_5}]\n") 
        print("-" * 60) 

def remove_subscription(drop_id, user="me"):
    """
    Unsubscribe from a drop_id.
    Return True if removed, False if not found.
    """
    subs = load_subs()
    initial_count = len(subs)

    # Filter out the subscription to be removed
    subs = [sub for sub in subs if not (sub['drop_id'] == drop_id and sub['user'] == user)]

    if len(subs) < initial_count:
        save_subs(subs)
        print(f"\n Unsubscribed from drop ID '{drop_id}'.\n")
        return True
    else:
        print(f"\n No subscription found for drop ID '{drop_id}'.\n")
        return False    

def interactive_mode():
    """
    Interactive subscription management.
    Allows you to subscribe to drops through a simple menu.
    """
    while True:
        print("\n" + "="*50)
        print("🔔 SNEAKER DROP SUBSCRIPTION MANAGER")
        print("="*50)
        print("1.  List available drops")
        print("2.  Subscribe to a drop")
        print("3.  List my subscriptions")
        print("4.  Remove subscription")
        print("5.  Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n--- AVAILABLE DROPS ---")
            list_drops_text()
        
        elif choice == "2":
            print("\n--- SUBSCRIBE TO A DROP ---")
            list_drops_text()  # Show drops first
            print("\n" + "-"*40)
            drop_id = input("Enter the drop_id you want to subscribe to: ").strip()
            if drop_id:
                add_subscription(drop_id)
            else:
                print(" No drop_id entered")
       
        elif choice == "3":
            print("\n--- MY SUBSCRIPTIONS ---")
            list_subs_text()
        
        elif choice == "4":
            print("\n--- REMOVE SUBSCRIPTION ---")
            list_subs_text()  # Show current subscriptions
            print("\n" + "-"*40)
            drop_id = input("Enter the drop_id to unsubscribe from: ").strip()
            if drop_id:
                remove_subscription(drop_id)
            else:
                print(" No drop_id entered")
        
        elif choice == "5":
            print("\n👋 Goodbye! Happy sneaker hunting!")
            break
        
        else:
            print(" Invalid choice, please try again")

def main():
    """
    Demonstration of subscription management functions.
    Shows how the functions would be called programmatically.
    """
    print("=== Sneaker Drop Subscription Manager ===\n")
    
    # Example 1: List all available drops
    print("--- LISTING ALL DROPS ---")
    list_drops_text()
    
    # Example 2: Subscribe to a drop (you'd replace with actual drop_id)
    print("\n--- SUBSCRIBING TO A DROP ---")
    # Uncomment and replace with real drop_id when ready:
    # add_subscription("air-jordan-1-retro-high-og-2025-01-15", user="me")
    print("(Use: add_subscription('drop_id_here') to subscribe)")
    
    # Example 3: List all subscriptions
    print("\n--- LISTING SUBSCRIPTIONS ---")
    list_subs_text()
    
    # Example 4: Remove a subscription
    print("\n--- REMOVING A SUBSCRIPTION ---")
    # Uncomment to test removal:
    # remove_subscription("air-jordan-1-retro-high-og-2025-01-15", user="me")
    print("(Use: remove_subscription('drop_id_here') to unsubscribe)")
    
    print("\n✓ Subscription management demo complete")

if __name__ == '__main__':
    interactive_mode()
    