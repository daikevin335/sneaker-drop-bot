import json 
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import sys

# Add parent directory to path to import other modules
sys.path.append(str(Path(__file__).resolve().parent.parent))
from bot.storage import load_drops, load_subs, save_subs
from bot.reminders import get_current_time, process_reminders, due_stages
from bot.notify import send_reminder

# Configuration file path
CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.json"

def load_config() -> dict:
    """
    Load configruation from config.json file.
    Returns default config if file doesn't exist or has errors.
    """
    default_config = {
        "timezone": "America/Toronto",
        "discord_webhook": "",
        "brand_filters": []
    }

    # If config file DNE, return default
    if not CONFIG_FILE.exists():
        print("No config.json found using default configuration.")
        return default_config
    
    # Try to load and parse config file
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"Loaded config from {CONFIG_FILE}")
        return config
    except Exception as e:
        print(f"Error loading config.json: {e}. Using default configuration.")
        return default_config
    
def run_single_check():
    """
    Run a single reminder check: load data, process reminders, save if changed.
    Core function that does one complete pass of reminder system.
    """
    print("=== Sneaker Drop Reminder Check ===\n")

    # Load configuration 
    config = load_config()
    webhook_url = config.get("discord_webhook", "").strip()

    # If no webhook URL, abort
    if not webhook_url:
        print("No Discord webhook URL configured in config.json.")
        print("Add 'discord_webhook': 'your_webhook_url' to config.json to enable reminders.")
        return False
    
    # Load data
    drops = load_drops()
    subs = load_subs()  

    if not drops: 
        print("No drops found. Please run scraper first.")  
        return False
    
    if not subs:
        print("No subscriptions found. use subscribe.py to add subscriptions.")
        return False
    
    print(f"Loaded {len(drops)} drops and {len(subs)} subscriptions.\n")

    # Get current time
    now = get_current_time()
    print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # Process reminders
    print("\nProcessing reminders...")
    print("\nProcessing reminders...")
    updated_subs, changed = process_reminders(
        drops=drops,
        subs=subs,
        config=config,
        now=now,
        send_fn=send_reminder
    )

    # Save changes if ant reminders were sent 
    if changed:
        save_subs(updated_subs)
        print("\nSubscriptions updated with sent reminders.")
    else:
        print("\nNo reminders were due at this time.")

    print("\n✓ Reminder check complete.")
    return True

def run_continuous_loop(check_interval_seconds: int = 60):
    """
    Run reminder checks continuously in a loop.
    Checks every N seconds (default 60 seconds = 1 minute).
    
    Args:
        check_interval_seconds: How often to check for reminders (default 60s)
    
    Note: This is for demonstration. In production, you'd use:
    - Cron job: */1 * * * * (every minute)
    - Systemd timer
    - Task scheduler
    - Or run this script in background with nohup
    """
    print(f"=== Continuous Reminder Loop (every {check_interval_seconds}s) ===")
    print("Press Ctrl+C to stop\n")
    
    import time

    try:
        while True:
            print(f"\n--- Check at {datetime.now().strftime('%H:%M:%S')} ---")
            run_single_check()
            
            print(f"Waiting {check_interval_seconds} seconds until next check...")
            time.sleep(check_interval_seconds)
    
    except KeyboardInterrupt:
        print("\n\n Stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n Error in continuous loop: {e}")


def main():
    """
    Main entry point for running reminder checks.
    Runs a single check by default."
    """
    print("=== Sneaker Drop Reminder Bot ===\n")
    
    # Run single check
    success = run_single_check()
    
    if not success:
        print("\n Reminder check failed")
        return
    
    print("\n" + "="*50)
    print("USAGE OPTIONS:")
    print("="*50)
    print("1. Single check (what we just did):")
    print("   python bot/run_reminders.py")
    print()
    print("2. Continuous loop (every 60 seconds):")
    print("   python bot/run_reminders.py --loop")
    print()
    print("3. Custom interval (every 30 seconds):")
    print("   python bot/run_reminders.py --loop 30")
    print()
    print("4. Production deployment options:")
    print("   # Cron job (every minute):")
    print("   */1 * * * * cd /path/to/sneaker-drop-bot && python bot/run_reminders.py")
    print()
    print("   # Systemd timer (Linux):")
    print("   # Create /etc/systemd/system/sneaker-reminders.service")
    print("   # Create /etc/systemd/system/sneaker-reminders.timer")
    print()
    print("   # Background process:")
    print("   nohup python bot/run_reminders.py --loop > reminders.log 2>&1 &")
    print()
    print("✓ Setup complete!")

if __name__ == '__main__':
    import sys
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--loop':
            # Continuous loop mode
            interval = 60  # default
            if len(sys.argv) > 2:
                try:
                    interval = int(sys.argv[2])
                except ValueError:
                    print(" Invalid interval, using 60 seconds")
            
            run_continuous_loop(interval)
        else:
            print(" Unknown argument. Use --loop [seconds] for continuous mode")
    else:
        # Single check mode (default)
        main()
    
            

