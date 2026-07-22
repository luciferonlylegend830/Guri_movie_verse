from telethon import TelegramClient
import json

# अपनी डिटेल्स यहाँ भरें (my.telegram.org से लें)
api_id = '36304765'  # यहाँ अपना API ID डालें
api_hash = '449c24a0a125276520b2b0bf3d93bf2c'  # यहाँ अपना API HASH डालें
client = TelegramClient('anon', api_id, api_hash)

async def main():
    # चैनल की ID डालें (-1002748829128)
    channel_username = -1002748829128
    movies = {}
    # चैनल के सभी मैसेज को स्कैन करेगा
    print("Scanning channel...")
    async for message in client.iter_messages(channel_username):
        if message.video or message.document:
            caption_text = message.text or ""
            file_name = caption_text.split('\n')[0] if caption_text else "Unknown Movie"
            file_id = message.video.file_id if message.video else message.document.file_id
            
            movies[file_name.lower()] = {
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
    
