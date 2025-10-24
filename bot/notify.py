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
    
