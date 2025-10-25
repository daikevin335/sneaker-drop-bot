# Sneaker Drop Tracker Bot

A Python automation tool that keeps sneaker enthusiasts ahead of the game.
Inspired by missing too many drops myself, I built this Discord bot to scrape sneaker release data, manage subscriptions, and send timed notifications — turning a personal frustration into a practical backend project.

##  Features

- **Automated Scraping**: Fetches sneaker release data from SneakerNews
- **Smart Reminders**: Sends Discord notifications at T-24h, T-1h, T-30min, T-15min, and T-5min before drops
- **Subscription Management**: Subscribe to specific drops you're interested in
- **Rich Notifications**: Color-coded Discord embeds with sneaker images and store links
- **Timezone Support**: All times handled in America/Toronto timezone
- **No Auto-Buy**: Ethical approach - reminders only, no automated purchasing

##  How It Works

1. **Scraping**: Bot scrapes SneakerNews for upcoming releases and saves to `drops.csv`
2. **Subscription**: Users subscribe to specific drops via interactive terminal menu
3. **Reminders**: Bot checks for due reminders every minute and sends Discord notifications
4. **Tracking**: Remembers which reminders were sent to avoid duplicates

##  File Structure

sneaker-drop-bot/

├── bot/

│ ├── storage.py # CSV/JSON data handling

│ ├── scrape.py # Web scraping for sneaker releases

│ ├── subscribe.py # Interactive subscription management CLI

│ ├── notify.py # Discord webhook notifications with images

│ ├── reminders.py # Reminder logic and time calculations

│ └── run_reminders.py # Main runner and entry point

├── config.json # Configuration (webhook, timezone, filters)

├── drops.csv # Scraped sneaker releases (auto-generated)

├── subscriptions.json # User subscriptions (auto-generated)

└── requirements.txt # Python dependencies

##  Configuration

Create `config.json` in the project root:

```json
{
  "timezone": "America/Toronto",
  "discord_webhook": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN",
  "brand_filters": ["Nike", "Adidas", "Jordan"]
}
```

### Getting Discord Webhook URL:
1. Go to your Discord server
2. Right-click a channel → Edit Channel → Integrations → Webhooks
3. Create a webhook and copy the URL
4. Paste it in `config.json`

##  Usage
### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create config.json (see Configuration section above)
```

### 2. Scrape Releases
```bash
# Run scraper to get latest drops
python bot/scrape.py
```

### 3. Subscribe to Drops
```bash
# Interactive subscription manager
python bot/subscribe.py
```
**Interactive Menu:**
- **1. List available drops** - See all scraped sneaker releases
- **2. Subscribe to a drop** - Pick a drop_id and subscribe
- **3. List my subscriptions** - See what you're subscribed to
- **4. Remove subscription** - Unsubscribe from a drop
- **5. Exit** - Close the program

### 4. Run Reminders
```bash
# Single check
python bot/run_reminders.py

# Continuous loop (every 60 seconds)
python bot/run_reminders.py --loop

# Custom interval (every 30 seconds)
python bot/run_reminders.py --loop 30
```

##  Reminder Schedule

The bot sends **5 different reminder types**:

| Time Before Drop | Reminder Type | Color | Purpose |
|------------------|---------------|-------|---------|
| **24 hours** | 📅 Sneaker Drop Tomorrow | Blue | Advance planning |
| **1 hour** | ⏰ Sneaker Drop in 1 Hour | Orange | Final preparation |
| **30 minutes** | 🚨 Sneaker Drop in 30 min | Green | Get ready |
| **15 minutes** | 🚨 Sneaker Drop in 15 min | Orange | Almost time |
| **5 minutes** | 🚨 Sneaker Drop in 5 min | Red | Final warning |


##  Extending the Bot

### Adding New Scraping Sources
1. Modify `bot/scrape.py` to add new website selectors
2. Update the parsing logic for different site structures
3. Ensure consistent data format (drop_id, name, brand, drop_iso, url)

 ### Adding Brand Filters
Update `config.json` to filter specific brands:
```json
{
  "brand_filters": ["Nike", "Adidas", "Jordan", "New Balance"]
}
```

### Custom Reminder Times
Modify `bot/reminders.py` in the `due_stages()` function:
```python
# Add custom reminder windows
if 120 <= minutes_left < 121:  # 2 hours before
    due.append("120")
```

## NOTES
This not is designed for **reminders only** - it does not: 
- Automatically make purchaes
- Bypass purchase limits or queues
- Violate website terms of services
- Perform any automated buy actions

  
I DO NOT ENCOURAGE ANY ACT OF SCALPING !! 😡
The bot respects ethical boundaries and is intended to help users stay informed about releases they're genuinely interested in.

##  Dependencies

- `requests` - HTTP requests for web scraping and Discord webhooks
- `beautifulsoup4` - HTML parsing for sneaker release data
- `pandas` - Data manipulation (optional, for CSV handling)
- `python-dateutil` - Advanced date parsing and timezone handling


This is a personal project, but feel free to fork and adapt for your own use. Remember to respect website terms of service and ethical automation practices. 🙂
