import os
import yt_dlp
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# ==============================
# TOKEN
# ==============================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN NOT FOUND!")

# ==============================
# Web Server (Render)
# ==============================
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('', port), Handler)
    server.serve_forever()

threading.Thread(target=run_server).start()

# ==============================
# START COMMAND
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك\n\n"
        "📥 أرسل رابط فيديو وسأقوم بتحميله بأفضل جودة ممكنة"
    )

# ==============================
# التحقق من الرابط
# ==============================
def is_url(text):
    return text.startswith("http://") or text.startswith("https://")

# ==============================
# إعدادات yt-dlp (مستقرة)
# ==============================
def get_ydl_opts():
    return {
        'format': 'bestvideo+bestaudio/best',  # متوافق مع كل المواقع
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'merge_output_format': 'mp4',
        'noplaylist': True,
    }

# ==============================
# تحميل الفيديو
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # إذا مو رابط
    if not is_url(text):
        await update.message.reply_text("❗ أرسل رابط فيديو صحيح")
        return

    await update.message.reply_text("⏬ جاري التحميل...")

    try:
        ydl_opts = get_ydl_opts()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            filename = "video.mp4"

        if os.path.exists(filename):
            size = os.path.getsize(filename)

            if size > 50 * 1024 * 1024:
                await update.message.reply_text("📎 الفيديو كبير:")
                await update.message.reply_text(text)
            else:
                await update.message.reply_video(video=open(filename, 'rb'))
        else:
            raise Exception("Download failed")

    except Exception as e:
        print("ERROR:", e)

        # fallback
        try:
            await update.message.reply_text("🔁 محاولة بطريقة أخرى...")

            with yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': 'video.%(ext)s'}) as ydl:
                ydl.download([text])

            await update.message.reply_video(video=open("video.mp4", 'rb'))

        except:
            await update.message.reply_text("❌ لا يمكن تحميل هذا الفيديو")

# ==============================
# تشغيل البوت
# ==============================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("🚀 Bot is running...")

app.run_polling()
