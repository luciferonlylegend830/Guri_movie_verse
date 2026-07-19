import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8942349455:AAGrcoY16mYheXkze0dha6pelgaZUuJ7HjU"
CHANNEL_ID = -1002748829128 # Guri Movies Verse Channel ID

# मूवीज को स्टोर करने के लिए एक टेम्परेरी मेमोरी (डिक्शनरी)
movie_database = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("हेलो भाई! मैं चालू हूँ। ग्रुप में मूवी का नाम सर्च करो।")

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
            # कैप्शन के छोटे अक्षरों में सेव करेंगे ताकि सर्च आसान हो
            movie_database[caption_text.lower()] = {
                "file_id": file_id,
                "file_type": file_type,
                "file_name": file_name
            }
            logging.info(f"Saved movie: {file_name}")

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip().lower()
    if len(query) < 3:
        return

    found = False
    # अपनी सेव की हुई मेमोरी में सर्च करना
    for caption, data in movie_database.items():
        if query in caption:
            new_caption = f"🎬 **{data['file_name']}**\n\n📢 **Joined: @Guri_movies_verse**\n🍿 **Enjoy Your Movie!**"
            
            if data['file_type'] == "video":
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=data['file_id'],
                    caption=new_caption,
                    parse_mode="Markdown"
                )
            elif data['file_type'] == "document":
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=data['file_id'],
                    caption=new_caption,
                    parse_mode="Markdown"
                )
            found = True
            break
            
    if not found:
        # अगर डेटाबेस में न मिले, तो यह पुराना तरीका बैकअप के लिए ट्राई करेगा
        try:
            messages = await context.bot.get_chat_history(chat_id=CHANNEL_ID, limit=30)
            for message in messages:
                c_text = message.caption if message.caption else (message.text if message.text else "")
                if query in c_text.lower():
                    f_name = message.document.file_name if message.document else (message.video.file_name if message.video and message.video.file_name else query.capitalize())
                    new_caption = f"🎬 **{f_name}**\n\n📢 **Joined: @Guri_movies_verse**\n🍿 **Enjoy Your Movie!**"
                    
                    if message.video:
                        await context.bot.send_video(chat_id=update.effective_chat.id, video=message.video.file_id, caption=new_caption, parse_mode="Markdown")
                    elif message.document:
                        await context.bot.send_document(chat_id=update.effective_chat.id, document=message.document.file_id, caption=new_caption, parse_mode="Markdown")
                    found = True
                    break
        except Exception as e:
            logging.error(f"Backup search failed: {e}")
            
        if not found:
            await update.message.reply_text("🔍 भाई, यह मूवी चैनल में नहीं मिली या बॉट अभी लोड कर रहा है। कृपया नाम सही से लिखें।")

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
                    
