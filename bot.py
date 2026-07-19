import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8942349455:AAGrcoY16mYheXkze0dha6pelgaZUuJ7HjU"
CHANNEL_ID = -1002242502830 # Guri Movies Verse Channel ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("हेलो भाई! मैं चालू हूँ। ग्रुप में मूवी का नाम सर्च करो।")

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip().lower()
    if len(query) < 3:
        return

    try:
        messages = await context.bot.get_chat_history(chat_id=CHANNEL_ID, limit=50)
        found = False
        
        for message in messages:
            caption_text = ""
            if message.caption:
                caption_text = message.caption
            elif message.text:
                caption_text = message.text
            
            if query in caption_text.lower():
                file_name = ""
                if message.document:
                    file_name = message.document.file_name
                elif message.video:
                    file_name = message.video.file_name if message.video.file_name else "Movie File"
                else:
                    file_name = query.capitalize()

                new_caption = f"🎬 **{file_name}**\n\n📢 **Joined: @Guri_movies_verse**\n🍿 **Enjoy Your Movie!**"

                if message.video:
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=message.video.file_id,
                        caption=new_caption,
                        parse_mode="Markdown"
                    )
                elif message.document:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=message.document.file_id,
                        caption=new_caption,
                        parse_mode="Markdown"
                    )
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=new_caption,
                        parse_mode="Markdown"
                    )
                
                found = True
        
        if not found:
            await update.message.reply_text("🔍 भाई, यह मूवी चैनल में नहीं मिली। कृपया नाम सही से लिखें।")
            
    except Exception as e:
        logging.error(f"Search Error: {e}")
        await update.message.reply_text("⚠ सर्च करते समय एक खराबी आई। कृपया पक्का करें कि बॉट आपके चैनल में एडमिन है।")

async def handle(request):
    return web.Response(text="Bot is running smoothly!")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    
    await app.initialize()
    await app.start()
    print("Bot started...")
    await app.updater.start_polling()
    
    # वेब सर्वर सेटअप (बिना किसी स्पेस एरर के)
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
                        
