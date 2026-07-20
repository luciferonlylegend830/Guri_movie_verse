import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient
MONGO_URI = "mongodb+srv://luciferonlylegend830_db_user:GuriSingh@123@guricluster.f3ytryg.mongodb.net/?retryWrites=true&w=majority&appName=GURICLUSTER"
client = AsyncIOMotorClient(MONGO_URI)
db = client['GURICLUSTER']
movies_col = db['movies']
async def delete_message_after_delay(context, chat_id, message_id):
    await asyncio.sleep(300) # 5 मिनट का वेट
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.error(f"Error deleting message: {e}")
        
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8942349455:AAGrcoY16mYheXkze0dha6pelgaZUuJ7HjU"
CHANNEL_ID = -1002748829128 # Guri Movies Verse Channel ID
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("hello guys! I'm wakeup Find your movie in the group.")

# जब चैनल में नई पोस्ट आएगी, बॉट उसे यहाँ सेव कर लेगा
async def save_channel_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if not message:
        return
        
    caption_text = ""
    if message.caption:
        caption_text = message.caption
    elif message.text:
        caption_text = message.text
        
    if caption_text:
        file_id = None
        file_type = None
        file_name = caption_text.split('\n')[0] # पहली लाइन को नाम मानेंगे
        
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
                {"caption": caption_text.lower()},
                {"$set": {"file_id": file_id, "file_type": file_type, "file_name": file_name}},
                upsert=True
                        )
            
            logging.info(f"Saved movie: {file_name}")

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip().lower()
# 1. सुरक्षा: अगर सर्च 5 अक्षरों से छोटी है
    if len(query) < 5:
        await update.message.reply_text("❌ कृपया कम से कम 5 अक्षरों का नाम लिखें।")
        return
 # डेटाबेस से सर्च करें
    results = await movies_col.find({"caption": {"$regex": query, "$options": "i"}}).to_list(length=10)
    # 2. अगर कोई रिजल्ट नहीं मिला
    if not results:
        await update.message.reply_text("❌ Sorry, this movie was not found.")
        return
  # 3. सुरक्षा: सिर्फ पहली 1 मूवी भेजें
        data = results[0] 
    if data['file_type'] == "video":
        sent_msg = await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=data['file_id'],
            caption=f"🎬 **{data['file_name']}**\n🔗 Join: @GuriMoviesVerse 🍿🎥\n⚠️ This file will be auto-deleted in 5 minutes."
        )
        asyncio.create_task(delete_message_after_delay(context, update.effective_chat.id, sent_msg.message_id))
    elif data['file_type'] == "document":
        sent_msg = await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=data['file_id'],
            caption=f"🎬 **{data['file_name']}**\n🔗 Join: @GuriMoviesVerse 🍿🎥\n⚠️ This file will be auto-deleted in 5 minutes."
        )
        asyncio.create_task(delete_message_after_delay(context, update.effective_chat.id, sent_msg.message_id))
        
        

async def handle(request):
    return web.Response(text="Bot is running smoothly!")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # यह हैंडलर चैनल की नई पोस्ट्स को मॉनिटर करेगा
    app.add_handler(MessageHandler(filters.Chat(chat_id=CHANNEL_ID), save_channel_posts))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    
    await app.initialize()
    await app.start()
    print("Bot started...")
    await app.updater.start_polling()
    
    app_web = web.Application()
    app_web.router.add_get('/', handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 10000)))
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
