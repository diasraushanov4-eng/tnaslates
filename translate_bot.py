#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Inline Translation Bot - OPTIMIZED VERSION
Tez va samarali tarjima bot
"""

import logging
import os
import threading
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, InlineQueryHandler, CommandHandler, ContextTypes
from deep_translator import GoogleTranslator
import uuid
from flask import Flask, jsonify

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app (Health check uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>Translation Bot</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🤖 Bot is Running!</h1>
        <p>✅ Translation bot is active and ready</p>
        <p>📱 Use the bot in Telegram</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": "running"})

def run_flask():
    """Flask serverni alohida thread'da ishga tushirish"""
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Til kodlari va ularning barcha variantlari (JUDAham ko'p!)
LANGUAGE_VARIANTS = {
    'ru': ['ru', 'rus', 'russian', 'russia', 'русский', 'russkiy', 'рус', 'russkaya', 'rossiya', 'ruscha'],
    'en': ['en', 'eng', 'english', 'ingliz', 'английский', 'англ', 'inglizcha', 'ingiliz', 'england'],
    'uz': ['uz', 'uzb', 'uzbek', "o'zbek", 'ozbek', 'узбекский', 'ўзбек', 'ozbekcha', 'uzbekcha'],
    'tr': ['tr', 'tur', 'turk', 'turkish', 'turkcha', 'türkçe', 'турецкий', 'turkiye', 'turkiy'],
    'de': ['de', 'deu', 'ger', 'german', 'nemis', 'deutsch', 'немецкий', 'germaniya', 'nemischa', 'olmon'],
    'fr': ['fr', 'fra', 'fre', 'french', 'fransuz', 'français', 'francais', 'французский', 'fransiya', 'fransuzcha'],
    'es': ['es', 'spa', 'spanish', 'ispan', 'español', 'espanol', 'испанский', 'ispaniya', 'ispancha'],
    'ar': ['ar', 'ara', 'arabic', 'arab', 'عربي', 'арабский', 'arabcha', 'arabiya', 'arabiy'],
    'zh': ['zh', 'chi', 'zho', 'chinese', 'xitoy', '中文', 'китайский', 'china', 'xitoycha', 'xitoy tili'],
    'ja': ['ja', 'jpn', 'japanese', 'yapon', '日本語', 'японский', 'japan', 'yaponcha', 'yapon tili', 'yaponiy'],
    'ko': ['ko', 'kor', 'korean', 'koreys', '한국어', 'корейский', 'korea', 'koreycha', 'koreyscha', 'koreys tili'],
    'it': ['it', 'ita', 'italian', 'italyan', 'italiano', 'итальянский', 'italiya', 'italyancha', 'italy'],
    'pt': ['pt', 'por', 'portuguese', 'portugal', 'português', 'portugues', 'португальский', 'portugalcha', 'portugaliya'],
    'hi': ['hi', 'hin', 'hindi', 'hind', 'हिन्दी', 'хинди', 'hindiston', 'hindcha', 'hind tili', 'hindiy'],
    'pl': ['pl', 'pol', 'polish', 'polsha', 'polski', 'польский', 'polcha', 'polsha tili', 'poland'],
    'uk': ['uk', 'ukr', 'ukrainian', 'ukraina', 'українська', 'украинский', 'ukrain', 'ukraincha', 'ukraina tili'],
    'nl': ['nl', 'dut', 'nld', 'dutch', 'golland', 'nederlands', 'голландский', 'niderland', 'gollandcha', 'gollandiya'],
    'sv': ['sv', 'swe', 'swedish', 'shved', 'svenska', 'шведский', 'shvetsiya', 'shvedcha', 'sweden'],
    'cs': ['cs', 'cze', 'ces', 'czech', 'chex', 'čeština', 'чешский', 'chexiya', 'chexcha', 'czech republic'],
    'vi': ['vi', 'vie', 'vietnamese', 'vyetnam', 'tiếng việt', 'вьетнамский', 'vyetnamcha', 'vietnam'],
    'th': ['th', 'tha', 'thai', 'tailand', 'ไทย', 'тайский', 'taycha', 'thailand', 'taylandcha'],
    'id': ['id', 'ind', 'indonesian', 'indoneziya', 'bahasa indonesia', 'индонезийский', 'indonezcha', 'indonesia'],
    'fa': ['fa', 'per', 'fas', 'persian', 'fors', 'فارسی', 'персидский', 'eron', 'forscha', 'iran', 'forsi'],
    'ro': ['ro', 'rum', 'ron', 'romanian', 'rumin', 'română', 'румынский', 'ruminiya', 'romania', 'rumincha'],
    'hu': ['hu', 'hun', 'hungarian', 'venger', 'magyar', 'венгерский', 'vengriya', 'hungary', 'venger tili'],
    'da': ['da', 'dan', 'danish', 'daniya', 'dansk', 'датский', 'daniyacha', 'denmark', 'daniya tili'],
    'fi': ['fi', 'fin', 'finnish', 'finlyandiya', 'suomi', 'финский', 'fincha', 'finland', 'finlyandiya tili'],
    'no': ['no', 'nor', 'norwegian', 'norvegiya', 'norsk', 'норвежский', 'norvegcha', 'norway', 'norvegiya tili'],
    'el': ['el', 'gre', 'ell', 'greek', 'yunon', 'ελληνικά', 'греческий', 'gretsiya', 'greece', 'yunoncha'],
    'he': ['he', 'heb', 'hebrew', 'ibroniy', 'עברית', 'иврит', 'yahudiy', 'israel', 'ibroniycha', 'ivrit'],
}

# Tillarning flag emoji
LANGUAGE_FLAGS = {
    'ru': '🇷🇺', 'en': '🇬🇧', 'uz': '🇺🇿', 'tr': '🇹🇷',
    'de': '🇩🇪', 'fr': '🇫🇷', 'es': '🇪🇸', 'ar': '🇸🇦',
    'zh': '🇨🇳', 'ja': '🇯🇵', 'ko': '🇰🇷', 'it': '🇮🇹',
    'pt': '🇵🇹', 'hi': '🇮🇳', 'pl': '🇵🇱', 'uk': '🇺🇦',
    'nl': '🇳🇱', 'sv': '🇸🇪', 'cs': '🇨🇿', 'vi': '🇻🇳',
    'th': '🇹🇭', 'id': '🇮🇩', 'fa': '🇮🇷', 'ro': '🇷🇴',
    'hu': '🇭🇺', 'da': '🇩🇰', 'fi': '🇫🇮', 'no': '🇳🇴',
    'el': '🇬🇷', 'he': '🇮🇱',
}

def detect_language_code(text: str) -> str:
    """Matndan til kodini aniqlaydi"""
    text_lower = text.lower().strip()
    
    for lang_code, variants in LANGUAGE_VARIANTS.items():
        for variant in variants:
            if text_lower == variant:
                return lang_code
    
    return None


def parse_query(query: str) -> tuple:
    """Query ni parse qiladi"""
    parts = query.strip().split(maxsplit=1)
    
    if len(parts) < 2:
        return None, None
    
    lang_code = detect_language_code(parts[0])
    
    if lang_code and len(parts) > 1:
        return lang_code, parts[1]
    
    return None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi - English"""
    help_text = """
🌍 <b>Translation Bot</b>

<b>How to use:</b>

Type in any chat:
<code>@your_bot_name language_code text</code>

<b>Examples:</b>
• <code>@your_bot_name en Привет</code> → Hello
• <code>@your_bot_name ru Hello</code> → Привет
• <code>@your_bot_name korean Hello</code> → 안녕하세요
• <code>@your_bot_name koreyscha Hello</code> → 안녕하세요

<b>Supported languages (30+):</b>
🇬🇧 en, english, ingliz
🇷🇺 ru, russian, русский
🇺🇿 uz, uzbek, o'zbek
🇹🇷 tr, turkish, türkçe
🇰🇷 ko, korean, koreys, koreyscha, 한국어
🇯🇵 ja, japanese, yapon, yaponcha, 日本語
🇨🇳 zh, chinese, xitoy, xitoycha, 中文
🇩🇪 de, german, nemis, deutsch
🇫🇷 fr, french, fransuz, français
🇪🇸 es, spanish, ispan, español
🇸🇦 ar, arabic, arab, عربي
🇮🇹 it, italian, italyan, italiano
🇵🇹 pt, portuguese, portugal
🇮🇳 hi, hindi, hind, हिन्दी
🇵🇱 pl, polish, polsha, polski
🇺🇦 uk, ukrainian, ukraina
🇳🇱 nl, dutch, golland
🇸🇪 sv, swedish, shved
🇨🇿 cs, czech, chex
🇻🇳 vi, vietnamese, vyetnam
🇹🇭 th, thai, tailand, ไทย
🇮🇩 id, indonesian, indoneziya
🇮🇷 fa, persian, fors, فارسی
🇷🇴 ro, romanian, rumin
🇭🇺 hu, hungarian, venger
🇩🇰 da, danish, daniya
🇫🇮 fi, finnish, finlyandiya
🇳🇴 no, norwegian, norvegiya
🇬🇷 el, greek, yunon
🇮🇱 he, hebrew, ibroniy

<b>Fast | Simple | Free | 30+ Languages</b>
"""
    await update.message.reply_text(help_text, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help komandasi"""
    await start(update, context)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline query handler - OPTIMIZED"""
    query = update.inline_query.query
    
    # Bo'sh query
    if not query or len(query.strip()) == 0:
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="🌍 Translation Bot",
                description="Type: language_code text (Example: en Hello)",
                input_message_content=InputTextMessageContent(
                    "How to use:\n@bot_name language_code text\n\n"
                    "Example: @bot_name en Привет → Hello"
                ),
                thumb_url="https://i.imgur.com/5mxXj3L.png"
            )
        ]
        await update.inline_query.answer(results, cache_time=300)
        return
    
    # Query parse qilish
    target_lang, text = parse_query(query)
    
    if not target_lang or not text:
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="❌ Invalid format",
                description="Format: language_code text (Example: en Hello)",
                input_message_content=InputTextMessageContent(
                    "❌ Invalid format\n\n"
                    "Correct format:\n"
                    "@bot_name language_code text"
                )
            )
        ]
        await update.inline_query.answer(results, cache_time=0)
        return
    
    # FAQAT BITTA TILGA TARJIMA - TEZ!
    try:
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        
        flag = LANGUAGE_FLAGS.get(target_lang, '🌐')
        
        # Faqat 1 ta natija - maksimal tezlik!
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{flag} {translated_text}",
                description=f"Translate to {target_lang.upper()}",
                input_message_content=InputTextMessageContent(translated_text),
                thumb_url="https://i.imgur.com/5mxXj3L.png"
            )
        ]
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="❌ Translation failed",
                description="Please try again",
                input_message_content=InputTextMessageContent("Translation error. Please try again.")
            )
        ]
    
    # Tez javob qaytarish
    await update.inline_query.answer(results, cache_time=0)


def main():
    """Botni ishga tushirish"""
    TOKEN = os.getenv('8412558219:AAG1bblnF7ezEF6FjjlZE0KXv9FZZPzus3o', '8412558219:AAG1bblnF7ezEF6FjjlZE0KXv9FZZPzus3o')
    
    if TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("⚠️  BOT_TOKEN not set!")
        return
    
    # Flask server
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Telegram bot
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(InlineQueryHandler(inline_query))
    
    logger.info("🤖 Bot started - OPTIMIZED MODE")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
