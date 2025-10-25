from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Tuple, Callable
import sys
from pathlib import Path

# Add parent directory to path to be able to import storage
sys.path.append(str(Path(__file__).resolve().parent.parent))
from bot.storage import load_drops, load_subs, save_subs 

TARGET_TZ = ZoneInfo("America/Toronto")

def due_stages(now: datetime, drop_dt: datetime) -> List[Tuple[str, int]]:
    """
    Calculate which reminder stages are due based on current time vs drop time.
    
    Args:
        now: Current datetime (should be timezone-aware)
        drop_dt: Drop datetime (should be timezone-aware)
    
    Returns:
        List of stage names that are due: ["30"], ["15"], ["5"], or []
    
    Time math logic:
    - T-30: Between 30-31 minutes before drop
    - T-15: Between 15-16 minutes before drop  
    - T-5: Between 5-6 minutes before drop
    - Uses 1-minute windows to avoid duplicate sends
    """
    # If drop time already passed, no stages are due
    if drop_dt <= now:
        return []

    # Calculate time difference in mins
    time_diff = drop_dt - now
    min_left = int(time_diff.total_seconds() / 60)

    # Determine due stages
    due = []

    # Check each stage  with 1-min windows
    if 30 <= min_left < 31:
        due.append("30")
    elif 15 <= min_left < 16:
        due.append("15")
    elif 5 <= min_left < 6:
        due.append("5")

    return due

def process_reminders(drops: List[Dict[str, str]], subs: List[Dict[str, Any]], 
                      config: Dict[str, Any], now: datetime, 
                      send_fn: Callable[[str, str, str, str, int, str], bool]) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Process all subscriptions and send due reminders.
    
    Args:
        drops: List of drop dictionaries from CSV
        subs: List of subscription dictionaries from JSON
        config: Configuration dict with webhook_url, etc.
        now: Current datetime for time calculations
        send_fn: Function to call for sending notifications (send_reminder)
    
    Returns:
        Tuple of (updated_subs, changed_flag)
        - updated_subs: Modified subscriptions with sent flags updated
        - changed_flag: True if any reminders were sent (for saving)
    """

    # Create lookup for drops by drop_id
    drops_dict = {drop['drop_id']: drop for drop in drops}

    updated_subs = []
    changed = False
 
    # Process each subscription
    for sub in subs:
        drop_id = sub.get('drop_id')
        user = sub.get('user')
        reminders_sent = sub.get('reminders_sent', {})
    
        # Find the corresponding drop
        drop = drops_dict.get(drop_id)
        if not drop: 
            print(f"Drop ID '{drop_id}' for user '{user}' not found in drops data.")
            updated_subs.append(sub) # Keep subscription unchanged
            continue 

        # Parse drop datetime
        try: 
            drop_dt = datetime.fromisoformat(drop['drop_iso'])
        except (ValueError, KeyError) as e:
            print(f"Invalid drop_iso for drop ID '{drop_id}': {e}")
            updated_subs.append(sub)
            continue

        # Check which stages are due
        due_stages_list = due_stages(now, drop_dt)

        if not due_stages_list:
            # No reminders due, keep subscriptions unchanged
            updated_subs.append(sub)
            continue 

        # Send notifcations for due stages
        for stage in due_stages_list:
            if reminders_sent.get(stage, False):
                print(f" Skipping {stage}min reminder for user '{user}' (already sent).")
                continue # Already sent this stage 

            # Format drop time for display
            try:
                drop_time_str = drop_dt.strftime('%b %d, %Y %I:%M %p')
            except:
                drop_time_str = drop['drop_iso']

            # Calculate mins left for display
            mins_left = int((drop_dt - now).total_seconds() / 60)

            # Send the notif 
            success = send_fn(
                webhook_url=config.get('discord_webhook', ''),
                sneaker_name=drop.get('name', 'Unknown Sneaker'),
                brand=drop.get('brand', 'Unknown Brand'),
                drop_time=drop_time_str,
                minutes_left=mins_left,
                url=drop.get('url', '')
            )

            if success:
                # Mark as sent
                reminders_sent[stage] = True
                changed = True
                print(f"Sent {stage}min reminder for '{drop.get('name')}' to {user}")
            else:
                print(f"Failed to send {stage}min reminder for '{drop.get('name')}'")

        # Update the subscription with new reminder status
        updated_subs.append({
            **sub,
            'reminders_sent': reminders_sent
        })

    return updated_subs, changed
    
def get_current_time() -> datetime:
    """
    Get current time in target timezone.
    Helper functions to ensure consistent timezone handling.
    """
    return datetime.now(tz=TARGET_TZ)

def check_timezone_edges(now: datetime, drop_dt: datetime) -> Dict[str, Any]:
    """
    Debug helper to check timezone and edge cases.
    For troubleshooting timezone issues.

    Returns:
        Dict with timezone info and time differences.
    """
    time_diff = drop_dt - now
    mins_left = int(time_diff.total_seconds() / 60)

    # Return detailed info 
    return {
        'now_iso': now.isoformat(),
        'drop_iso': drop_dt.isoformat(),
        'minutes_left': mins_left,
        'timezone_now': str(now.tzinfo),
        'timezone_drop': str(drop_dt.tzinfo),
        'due_stages': due_stages(now, drop_dt),
        'is_past': drop_dt <= now,
        'is_future': drop_dt > now
    }

def main():
    """
    Demo of reminder processing functions.
    """
    print("=== Reminder Logic Demo ===")

    # Load test data
    drops = load_drops()
    subs = load_subs()

    print(f"Loaded {len(drops)} drops and {len(subs)} subscriptions")
    
    # Get current time 
    now = get_current_time()
    print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # Demo timezone edge checking 
    if drops: 
        sample_drop = drops[0]
        try:
            drop_dt = datetime.fromisoformat(sample_drop['drop_iso'])
            edge_info = check_timezone_edges(now, drop_dt)
            print(f"\nSample drop analysis")
            print(f"  Drop: {sample_drop.get('name', 'Unknown')}")
            print(f"  Drop time: {edge_info['drop_iso']}")
            print(f"  Minutes left: {edge_info['minutes_left']}")
            print(f"  Due stages: {edge_info['due_stages']}")
            print(f"  Is past: {edge_info['is_past']}")
        except Exception as e:
            print(f"Error analyzing sample drop: {e}")
    
    # Demo due_stages function
    print(f"\nDue stages calculation demo:")
    test_times = [
        now + timedelta(minutes=35),  # T-35 (no reminder due)
        now + timedelta(minutes=30),  # T-30 (30min reminder due)
        now + timedelta(minutes=20),  # T-20 (no reminder due)
        now + timedelta(minutes=15), # T-15 (15min reminder due)
        now + timedelta(minutes=10),  # T-10 (no reminder due)
        now + timedelta(minutes=5),   # T-5 (5min reminder due)
        now + timedelta(minutes=1),  # T-1 (no reminder due)
    ]
    
    for test_dt in test_times:
        stages = due_stages(now, test_dt)
        minutes = int((test_dt - now).total_seconds() / 60)
        print(f"  T-{minutes:2d}: {stages if stages else 'No reminders due'}")
    
    print(f"\n✓ Reminder logic demo complete")

if __name__ == '__main__':
    main()
