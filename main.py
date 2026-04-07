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
# Web Server (Render fix)
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
# إعدادات السرعة + الجودة
# ==============================
def get_ydl_opts():
    return {
        # أولاً نحاول ملف جاهز mp4 (سريع)
        # وإذا ماكو → أعلى جودة ممكنة
        'format': 'best[ext=mp4]/bestvideo+bestaudio/best',

        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,

        # تسريع التحميل
        'noplaylist': True,
        'concurrent_fragment_downloads': 5,

        # تقليل الدمج قدر الإمكان
        'merge_output_format': 'mp4',

        # تحسين التوافق مع المواقع
        'http_headers': {
            'User-Agent': 'Mozilla/5.0',
        },

        # تجاوز بعض القيود
        'geo_bypass': True,
        'geo_bypass_country': 'US',
    }

# ==============================
# عند إرسال رابط
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⚡ جاري التحميل بأقصى سرعة وأعلى جودة...")

    try:
        ydl_opts = get_ydl_opts()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إذا ما لقى الملف
        if not os.path.exists(filename):
            filename = "video.mp4"

        if os.path.exists(filename):
            size = os.path.getsize(filename)

            # إذا كبير
            if size > 50 * 1024 * 1024:
                await update.message.reply_text("📎 الفيديو كبير، هذا الرابط:")
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
