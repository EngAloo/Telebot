import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

import os
TOKEN = os.getenv("TOKEN")

user_links = {}

# جلب الجودات
def get_formats(url):
    ydl_opts = {'quiet': True}
    formats_list = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        for f in info['formats']:
            if f.get('height'):
                formats_list.append((f['format_id'], f"{f['height']}p"))

    return formats_list


# عند إرسال رابط
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.chat_id

    user_links[user_id] = url

    await update.message.reply_text("جاري جلب الجودات...")

    formats = get_formats(url)

    keyboard = []
    for f_id, quality in formats[:10]:  # أول 10 فقط
        keyboard.append([InlineKeyboardButton(quality, callback_data=f_id)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("اختر الجودة:", reply_markup=reply_markup)


# عند اختيار الجودة
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    format_id = query.data
    user_id = query.message.chat_id
    url = user_links.get(user_id)

    await query.message.reply_text("جاري التحميل...")

    ydl_opts = {
        'format': format_id,
        'outtmpl': 'video.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    file_path = "video.mp4"

    # إذا الحجم كبير
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
