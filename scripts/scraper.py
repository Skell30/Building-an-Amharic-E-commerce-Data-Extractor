from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd
import os



# Replace with your actual API credentials
api_id = '28044604'
api_hash = '46fe4bcaa7f4e0b24080e0a7b1980279'

# List of channels to scrape (just the usernames, not full URLs)
channels = ['Leyueqa', 'ZemenExpress', 'meneshayeofficial','sinayelj','helloomarketethiopia']  # Replace 'another_channel' with a real one

# Create a client session
client = TelegramClient('session_name', api_id, api_hash)

with client:
    for channel_username in channels:
        try:
            channel = client.get_entity(channel_username)
            messages = []

            history = client(GetHistoryRequest(
                peer=channel,
                limit=500,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            for msg in history.messages:
                messages.append({
                    'channel': channel_username,
                    'id': msg.id,
                    'date': msg.date,
                    'sender': msg.from_id.user_id if msg.from_id else None,
                    'message': msg.message
                })

            # Save to CSV for each channel
            df = pd.DataFrame(messages)
            df.to_csv(f'./data/{channel_username}_messages.csv', index=False)

            print(f"✅ Saved messages from {channel_username}")

        except Exception as e:
            print(f"❌ Failed to scrape {channel_username}: {e}")
