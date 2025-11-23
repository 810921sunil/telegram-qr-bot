import logging
import os
import threading
from io import BytesIO
import qrcode

from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# ---------- Config ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------- Simple HTTP server (Render ke liye port bind) ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"QR bot is running\n")


def start_http_server():
    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"HTTP server listening on port {port}")
    server.serve_forever()


# ---------- Telegram bot handlers ----------
def start(update, context):
    text = (
        "Namaste! 👋\n"
        "Mujhe koi bhi link ya text bhejo,\n"
        "main uska QR code bana kar tumhe bhej dunga. 🔳\n\n"
        "Example:\nhttps://google.com\nhttps://youtu.be/..."
    )
    update.message.reply_text(text)


def generate_qr(data: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
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
    msg = update.message

    # Agar message me URL entity hai to wahi nikal lo
    if msg.entities:
        for e in msg.entities:
            if e.type == "url":
                url = msg.text[e.offset : e.offset + e.length]
                msg.reply_text("QR code bana raha hoon... 🔄")
                qr_img = generate_qr(url)
                msg.reply_photo(photo=qr_img)
                return

    # warna pure text ka QR
    text = (msg.text or "").strip()
    if text:
        msg.reply_text("QR code bana raha hoon... 🔄")
        qr_img = generate_qr(text)
        msg.reply_photo(photo=qr_img)


def main():
    if not BOT_TOKEN or not BOT_TOKEN.strip():
        print("Error: BOT_TOKEN env var set nahi hai.")
        return

    # HTTP server background thread me start karo (Render ke port ke liye)
    threading.Thread(target=start_http_server, daemon=True).start()

    # Telegram bot start karo
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, handle_text))

    updater.start_polling()
    logger.info("Bot running on Render...")
    updater.idle()


if __name__ == "__main__":
    main()
