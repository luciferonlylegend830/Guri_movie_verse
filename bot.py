import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

# Database credentials
username = quote_plus("luciferonlylegend830_db_user")
password = quote_plus("Gurisingh@123")
cluster_url = "guricluster.f3ytryg.mongodb.net"
MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority"

# Database connection setup
client = AsyncIOMotorClient(MONGO_URI)
db = client["movie_database"] 
movies_col = db["movies"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8942349455:AAGWtwN5S2HEZTqC4tlwzZe1d5aLvfvgylE"
CHANNEL_ID = -1002748829128 

async def delete_message_after_delay(context, chat_id, message_id):
    await asyncio.sleep(300) 
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.error(f"Error deleting message: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am awake. Send me a movie name to search.")

async def save_channel_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if not message:
        return
        
    caption_text = message.caption or message.text or ""
    if not caption_text:
        return

    file_id = None
    file_type = None
    file_name = caption_text.split('\n')[0]

    if message.video:
        file_id = message.video.file_id
        file_type = "video"
        if message.video.file_name: 
            file_name = message.video.file_name
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
        if message.document.file_name: 
            file_name = message.document.file_name

    if file_id:
        await movies_col.update_one(
        {"file_id": file_id},
        {"$set": {"file_id": file_id, "file_name": file_name, "file_type": file_type, "caption": caption_text.lower()}},
        upsert=True
    )
async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    query = update.message.text.strip().lower()

    if not query:
        await update.message.reply_text("❌ Please enter a movie name.")
        return
        
    results = await movies_col.find({"caption": {"$regex": query, "$options": "i"}}).to_list(length=10)
    
    if not results:
        await update.message.reply_text("❌ Sorry, this movie was not found.")
        return

    data = results[0]
    caption = f"🎬 **{data.get('file_name', 'Movie')}**\n🔗 Join: @GuriMoviesVerse 🍿🎥\n⚠️ This file will be auto-deleted in 5 minutes."
    
    try:
        if data.get('file_type') == "video":
            sent_msg = await context.bot.send_video(chat_id=update.effective_chat.id, video=data['file_id'], caption=caption)
        else:
            sent_msg = await context.bot.send_document(chat_id=update.effective_chat.id, document=data['file_id'], caption=caption)
        
        asyncio.create_task(delete_message_after_delay(context, update.effective_chat.id, sent_msg.message_id))
    except Exception as e:
        logging.error(f"Error sending file: {e}")
        await update.message.reply_text("❌ Error sending the movie file.")

async def handle(request):
    return web.Response(text="Bot is running smoothly!")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Chat(chat_id=CHANNEL_ID), save_channel_posts))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    
    await app.initialize()
    await app.start()
    print("Bot started...")
    
    app_web = web.Application()
    app_web.router.add_get('/', handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 10000)))
    await site.start()
    
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
            
