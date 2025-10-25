import requests
from typing import Optional 

def send_notif(webhook_url: str, message: str, title: Optional[str] = None, url: Optional[str] = None) -> bool:
    """
    Send a simple text message to Discord via webhook.
    
    Discord webhooks allow you to send messages to a channel without OAuth or bot tokens.
    You just POST JSON to the webhook URL with a 'content' field.
    
    Args:
        webhook_url: The Discord webhook URL from channel settings
        message: The main message text to send
        title: Optional title/header for the message
        url: Optional URL link to include
    
    Returns:
        True if sent successfully, False otherwise
    """
    try: 
        # Build mesesage content
        content = ""
        if title: 
            content += f"**{title}**\n"  # Bold title
        content += message
        if url:
            content += f"\n{url}"  # Append URL if provided
        
        # Discord webhook payload - simple content field 
        payload = {
            "content": content
        }

        print(f"Sending notification to Discord webhook... {title or 'Message'}")

        # POST to webhook URL
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  # Raise error for bad responses

        print("Notification sent successfully.")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def send_discord_embed(webhook_url: str, title: str, description: str, url: Optional[str] = None, color: int = 0x00ff00, fields: Optional[list] = None, image_url: Optional[str] = None, thumbnail_url: Optional[str] = None) -> bool:
    """
    Send rich embed message to Discord via webhook.
    Args:
        webhook_url: The Discord webhook URL
        title: Embed title (large bold text at top)
        description: Main embed content/description
        url: Optional clickable URL for the title
        color: Color bar on left side (hex color as int, default green)
        fields: Optional list of {"name": "Field Name", "value": "Field Value"} dicts
        image_url: Optional large image URL for the embed
        thumbnail_url: Optional small thumbnail image URL
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Build the embed structure
        embed = {
            "title": title,
            "description": description,
            "color": color,  # Left border color (0x00ff00 = green, 0xff0000 = red, etc.)
        }
        
        if url:
            embed["url"] = url
        
        # Add custom fields (shown as Name: Value pairs)
        if fields:
            embed["fields"] = fields
        
        # Add images if provided
        if image_url:
            embed["image"] = {"url": image_url}
        if thumbnail_url:
            embed["thumbnail"] = {"url": thumbnail_url}
        
        # Discord webhook payload with embeds
        payload = {
            "embeds": [embed]
        }
        
        print(f"Sending Discord embed: {title}")
        
        # POST to webhook URL
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print("✓ Discord embed sent successfully")
        return True
        
    except requests.RequestException as e:
        print(f"Discord embed failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error sending Discord embed: {e}")
        return False

    
def send_reminder(webhook_url: str, sneaker_name: str, brand: str, drop_time: str, minutes_left: int, url: Optional[str] = None, image_url: Optional[str] = None) -> bool:
    """
    Send a formatted drop reminder to Discord.
    Helper function that wraps send_discord_embed with sneaker-specific formatting 

    Args:
        webhook_url: Discord webhook URL
        sneaker_name: Name of the sneaker
        brand: Brand (Nike, Adidas, etc.)
        drop_time: Human-readable drop time
        minutes_left: How many minutes until drop
        url: Optional link to purchase page
        image_url: Optional image URL for sneaker thumbnail
    
    Returns:
        True if sent successfully, False otherwise
    """
    # Choose colour based on urgency 
    if minutes_left <= 5:
        color = 0xFF0000  # Red for urgent
    elif minutes_left <= 15:
        color = 0xFFA500  # Orange for upcoming
    else:
        color = 0x00FF00  # Green for early reminder

    # Build descrption 
    description = f"🔥 **{sneaker_name}** drops in **{minutes_left} minutes**!"

    # Build fields for structured info
    fields = [
        {"name": "Brand", "value": brand, "inline": True},
        {"name": "Drop Time", "value": drop_time, "inline": True},
        {"name": "Minutes Left", "value": f"⏰ {minutes_left} min", "inline": True}
    ]

    # Call generic embed sender with image support
    return send_discord_embed(
        webhook_url=webhook_url,
        title=f"🚨 Sneaker Drop Reminder ({minutes_left} min)",
        description=description,
        url=url,
        color=color,
        fields=fields,
        image_url=image_url
    )

def send_1day_reminder(webhook_url: str, sneaker_name: str, brand: str, drop_time: str, url: Optional[str] = None, image_url: Optional[str] = None) -> bool:
    """
    Send a 1-day advance reminder for sneaker drops.
    Less urgent than the minute-based reminders.
    
    Args:
        webhook_url: Discord webhook URL
        sneaker_name: Name of the sneaker
        brand: Brand (Nike, Adidas, etc.)
        drop_time: Human-readable drop time
        url: Optional link to purchase page
        image_url: Optional image URL for sneaker thumbnail
    
    Returns:
        True if sent successfully, False otherwise
    """
    # Blue color for 1-day reminder (less urgent)
    color = 0x0099FF
    
    # Build description for 1-day reminder
    description = f"📅 **{sneaker_name}** drops **tomorrow** at {drop_time}!"
    
    # Build fields for structured info
    fields = [
        {"name": "Brand", "value": brand, "inline": True},
        {"name": "Drop Time", "value": drop_time, "inline": True},
        {"name": "Time Left", "value": "📅 ~24 hours", "inline": True}
    ]
    
    # Call generic embed sender
    return send_discord_embed(
        webhook_url=webhook_url,
        title=f"📅 Sneaker Drop Tomorrow - {sneaker_name}",
        description=description,
        url=url,
        color=color,
        fields=fields,
        image_url=image_url
    )

def main():
    """
    Demo of notification functions.
    Replace WEBHOOK_URL with your actual Discord webhook to test.
    """
    print("=== Discord Notification Demo ===\n")
    
    # NOTE: Get your webhook URL from Discord:
    # Server Settings > Integrations > Webhooks > New Webhook > Copy Webhook URL
    
    WEBHOOK_URL = "https://discord.com/api/webhooks/1431022592554307635/vJWFq9RQvSghdTe18F7CyB1mcWMHuAjvcg7MG6saLaWc6jiXqCeAq7pJin65EZWh7rhI"
    
    # ------- TEST FUNCTIONS BELOW -------
    # 1. Go to Discord server
    # 2. Right-click channel > Edit Channel > Integrations > Webhooks
    # 3. Create webhook and copy URL
    # 4. Paste URL into WEBHOOK_URL variable above
    # Uncomment test calls below
    # ------------------------------------
    
    # TEST 1: Simple text message
    # send_notif(WEBHOOK_URL, "Testing the sneaker drop bot!", title="TEST")
    
    # TEST 2: Rich embed
    #send_discord_embed(
    #     webhook_url=WEBHOOK_URL,
    #    title="Test Embed",
    #    description="This is a test embed with colors and fields!",
    #    url="https://example.com",
    #    color=0x00ff00,
    #    fields=[
    #        {"name": "Field 1", "value": "Value 1", "inline": True},
    #        {"name": "Field 2", "value": "Value 2", "inline": True}
    #    ]
    # )
    
    # TEST 3: Sneaker reminder with image
    # send_reminder(
    #     webhook_url=WEBHOOK_URL,
    #     sneaker_name="Air Jordan 1 Retro High OG",
    #     brand="Nike",
    #     drop_time="Jan 15, 2025 10:00 AM",
    #     minutes_left=30,
    #     url="https://sneakernews.com/example",
    #     image_url="https://example.com/jordan1-image.jpg"
    # )

    # TEST 4: 1-day advance reminder with real image
    # send_1day_reminder(
    #     webhook_url=WEBHOOK_URL,
    #     sneaker_name="Air Jordan 1 Retro High OG",
    #     brand="Nike",
    #     drop_time="Jan 15, 2025 10:00 AM",
    #     url="https://sneakernews.com/example",
    #     image_url="https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500&h=500&fit=crop"
    # )
    
if __name__ == '__main__':
    main()