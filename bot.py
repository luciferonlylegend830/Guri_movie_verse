import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8942349455:AAGrcoY16myHeXkzeOdha6pelgaZUuJ7HjU"
CHANNEL_ID = -1002242502830 # Guri Movies Verse Channel ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("हेलो भाई! मैं चालू हूँ। ग्रुप में मूवी का नाम सर्च करो।")

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip().lower()
    if len(query) < 3:
        return

    found = False
    try:
        async for message in context.application.bot.get_chat_history(chat_id=CHANNEL_ID, limit=100):
            caption = ""
            if message.caption:
                caption = message.caption.lower()
            elif message.text:
                caption = message.text.lower()
            
            if query in caption:
                await context.application.bot.copy_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=CHANNEL_ID,
                    message_id=message.message_id
                )
                found = True
        
        if not found:
            pass
            
    except Exception as e:
        logging.error(f"Search Error: {e}")
        await update.message.reply_text("⚠ सर्च करते समय एक खराबी आई। कृपया पक्का करें कि बॉट चैनल में Admin है।")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    app.run_polling()

if __name__ == '__main__':
    main()
  
