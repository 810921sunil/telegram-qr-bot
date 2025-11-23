import logging
import os
import qrcode
from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text(
        "Send me any link or text and I will generate a QR code! 🔳🙂"
    )

def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    bio = BytesIO()
    bio.name = "qr.png"
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

def handle_text(update, context):
    # Get actual text (even if Telegram shows preview)
    if update.message.entities:
        for e in update.message.entities:
            if e.type == "url":
                url = update.message.text[e.offset : e.offset + e.length]
                update.message.reply_text("QR code bana raha hoon... 🔄")
                qr_img = generate_qr(url)
                update.message.reply_photo(photo=qr_img)
                return

    # fallback for plain text
    text = update.message.text.strip()
    if text:
        update.message.reply_text("QR code bana raha hoon... 🔄")
        qr_img = generate_qr(text)
        update.message.reply_photo(photo=qr_img)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    
    # *** FIXED HANDLER ***
    dp.add_handler(MessageHandler(Filters.all, handle_text))

    updater.start_polling()
    print("Bot running on Render...")
    updater.idle()

if __name__ == "__main__":
    main()
