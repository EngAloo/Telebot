import os
import yt_dlp
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==============================
# TOKEN من Environment Variables
# ==============================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN NOT FOUND!")

# ==============================
# تشغيل Web Server لـ Render
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
# تخزين روابط المستخدمين
# ==============================
user_links = {}

# ==============================
# جلب الجودات
# ==============================
def get_formats(url):
    ydl_opts = {
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
    }

    formats_list = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            for f in info.get('formats', []):
                if f.get('height') and f.get('format_id'):
                    formats_list.append((f['format_id'], f"{f['height']}p"))

    except Exception as e:
        print("FORMAT ERROR:", e)

    return formats_list

# ==============================
# عند إرسال رابط
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.chat_id

    user_links[user_id] = url

    await update.message.reply_text("🔍 جاري جلب الجودات...")

    formats = get_formats(url)

    # إذا ماكو جودات
    if not formats:
        await update.message.reply_text("⚠️ لم يتم العثور على جودات، سيتم تحميل أفضل جودة تلقائياً...")
        await download_and_send(update, url, "best")
        return

    keyboard = []
    for f_id, quality in formats[:10]:
        keyboard.append([InlineKeyboardButton(quality, callback_data=f_id)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("🎬 اختر الجودة:", reply_markup=reply_markup)

# ==============================
# عند اختيار الجودة
# ==============================
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    format_id = query.data
    user_id = query.message.chat_id
    url = user_links.get(user_id)

    await query.message.reply_text("⏬ جاري التحميل...")

    await download_and_send(query.message, url, format_id)

# ==============================
# تحميل وإرسال الفيديو
# ==============================
async def download_and_send(message, url, format_id):
    ydl_opts = {
        'format': format_id,
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_path = "video.mp4"

        if os.path.exists(file_path):
            size = os.path.getsize(file_path)

            # إذا أكبر من 50MB
            if size > 50 * 1024 * 1024:
                await message.reply_text("📎 الفيديو كبير، هذا رابط التحميل:")
                await message.reply_text(url)
            else:
                await message.reply_video(video=open(file_path, 'rb'))
        else:
            await message.reply_text("❌ فشل التحميل")

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        await message.reply_text("❌ حدث خطأ أثناء التحميل، سيتم المحاولة بأفضل جودة...")
        
        # fallback
        try:
            with yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': 'video.%(ext)s'}) as ydl:
                ydl.download([url])

            await message.reply_video(video=open("video.mp4", 'rb'))

        except:
            await message.reply_text("❌ فشل التحميل بالكامل")

# ==============================
# تشغيل البوت
# ==============================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(CallbackQueryHandler(button_click))

print("🚀 Bot is running...")

app.run_polling()    # إذا الحجم كبير
    if os.path.exists(file_path) and os.path.getsize(file_path) > 50 * 1024 * 1024:
        await query.message.reply_text("الفيديو كبير، سيتم إرسال رابط تحميل...")
        await query.message.reply_text(url)
    else:
        await query.message.reply_video(video=open(file_path, 'rb'))


# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(CallbackQueryHandler(button_click))

app.run_polling()
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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
