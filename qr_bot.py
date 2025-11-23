import logging
import os
import qrcode
from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Token environment se aayega (Render par secure way)
BOT_TOKEN = os.environ.get("8033548750:AAEf0rOOeW58c7JcIoS3SweBQIaMj5YSAos")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update, context):
    text = (
        "Namaste! 👋\n"
        "Mujhe koi bhi *link* ya *text* bhejo,\n"
        "main uska QR code bana kar tumhe bhej dunga. 📷🔳\n\n"
        "Example:\n"
        "👉 https://google.com\n"
        "👉 https://youtube.com\n"
    )
    update.message.reply_text(text, parse_mode="Markdown")

def generate_qr(data: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
        error_correction=qrcode.constants.ERROR_CORRECT_L
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    bio = BytesIO()
    bio.name = "qrcode.png"
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

def handle_text(update, context):
    user_text = update.message.text.strip()
    if not user_text:
        update.message.reply_text("Kuch to bhejo yaar, link ya text 🙂")
        return

    update.message.reply_text("QR code bana raha hoon, 1 sec... 🔄")
    try:
        qr_img = generate_qr(user_text)
        update.message.reply_photo(photo=qr_img, caption="Ye raha tumhara QR code 🔳")
    except Exception as e:
        logger.error(f"QR gen error: {e}")
        update.message.reply_text("QR code banate time error aa gaya 😥. Thoda baad try karna.")

def error(update, context):
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    if not BOT_TOKEN or BOT_TOKEN.strip() == "":
        print("Error: BOT_TOKEN env var set nahi hai.")
        return

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_error_handler(error)

    updater.start_polling()
    print("Bot Render par chal raha hai... Ctrl+C yahan kaam nahi karega (server side).")
    updater.idle()

if __name__ == "__main__":
    main()
