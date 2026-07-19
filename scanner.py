from telethon import TelegramClient
import json

# अपनी डिटेल्स यहाँ भरें (my.telegram.org से लें)
api_id = '36304765'      # यहाँ अपना API ID डालें
api_hash = '449c24a0a125276520b2b0bf3d93bf2c'  # यहाँ अपना API HASH डालें
client = TelegramClient('anon', api_id, api_hash)

async def main():
    # चैनल की ID डालें (-1002748829128)
    channel_username = -1002748829128 
    movies = {}

    print("Scanning channel...")
    # चैनल के सभी मैसेज को स्कैन करेगा
    async for message in client.iter_messages(channel_username):
        if message.video or message.document:
            file_name = message.file.name or "Unknown Movie"
            file_id = message.file.id
            movies[message.text.lower() if message.text else "unknown"] = {
                "file_id": file_id,
                "file_type": "video" if message.video else "document",
                "file_name": file_name
            }
            print(f"Added: {file_name}")

    # सारी मूवीज़ को एक फाइल में सेव करेगा
    with open('movies.json', 'w') as f:
        json.dump(movies, f)
    print("Scan complete! All movies saved to movies.json.")

with client:
    client.loop.run_until_complete(main())
  
