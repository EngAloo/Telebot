import os
import yt_dlp
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ==============================
# TOKEN
# ==============================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN NOT FOUND!")

# ==============================
# Web Server (حل Render)
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
# إعدادات التحميل القوية
# ==============================
def get_ydl_opts():
    return {
        'format': 'bestvideo+bestaudio/best',  # أعلى جودة
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,

        # تحسين التوافق مع المواقع
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        },

        # تقليل مشاكل الحظر
        'geo_bypass': True,
        'geo_bypass_country': 'US',
    }

# ==============================
# عند إرسال رابط
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⏬ جاري تحميل الفيديو بأعلى جودة...")

    try:
        ydl_opts = get_ydl_opts()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

        # تأكد من الامتداد
        if not os.path.exists(filename):
            filename = "video.mp4"

        # تحقق من الحجم
        if os.path.exists(filename):
            size = os.path.getsize(filename)

            if size > 50 * 1024 * 1024:
                await update.message.reply_text("📎 الفيديو كبير، هذا رابط المشاهدة:")
                await update.message.reply_text(url)
            else:
                await update.message.reply_video(video=open(filename, 'rb'))
        else:
            await update.message.reply_text("❌ فشل تحميل الفيديو")

    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text("❌ فشل التحميل من هذا الرابط")

# ==============================
# تشغيل البوت
# ==============================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("🚀 Bot is running...")

app.run_polling()
