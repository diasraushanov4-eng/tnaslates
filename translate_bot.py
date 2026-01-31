#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Inline Translation Bot (Flask bilan - 24/7 uchun)
Har qanday chatda ishlaydi va matnni 30+ tilga tarjima qiladi
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

# Flask app (Health check uchun - Render.com uyquga ketmasligi uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>Telegram Translation Bot</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🤖 Bot Ishlayapti!</h1>
        <p>✅ Translation bot ishga tushgan va tayyor</p>
        <p>📱 Telegram'da botni ishlating</p>
        <hr>
        <small>Powered by Render.com</small>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "bot": "running",
        "message": "Bot ishlayapti ✅"
    })

def run_flask():
    """Flask serverni alohida thread'da ishga tushirish"""
    port = int(os.getenv('PORT', 10000))
    logger.info(f"🌐 Flask server ishga tushmoqda port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Til kodlari va ularning barcha variantlari
LANGUAGE_VARIANTS = {
    'ru': ['ru', 'rus', 'russian', 'russia', 'русский', 'rus tilida', 'на русском языке', 'russkiy', 'russkaya', 'рус'],
    'en': ['en', 'eng', 'english', 'ingliz', 'ingliz tilida', 'in english', 'английский', 'инглиз', 'англ'],
    'uz': ['uz', 'uzb', 'uzbek', 'uzbek tilida', "o'zbek", 'ozbek', 'узбекский', 'ўзбек', 'ozbekcha'],
    'tr': ['tr', 'tur', 'turk', 'turkish', 'turkcha', 'turk tilida', 'türkçe', 'турецкий', 'turkiye'],
    'de': ['de', 'deu', 'german', 'nemis', 'deutsch', 'немецкий', 'germaniya', 'olmon'],
    'fr': ['fr', 'fra', 'french', 'fransuz', 'français', 'francais', 'французский', 'fransiya'],
    'es': ['es', 'spa', 'spanish', 'ispan', 'español', 'espanol', 'испанский', 'ispaniya'],
    'ar': ['ar', 'ara', 'arabic', 'arab', 'عربي', 'арабский', 'arabcha', 'arabiya'],
    'zh': ['zh', 'chi', 'chinese', 'xitoy', '中文', 'китайский', 'china', 'xitoycha'],
    'ja': ['ja', 'jpn', 'japanese', 'yapon', '日本語', 'японский', 'japan', 'yaponcha'],
    'ko': ['ko', 'kor', 'korean', 'koreys', '한국어', 'корейский', 'korea', 'koreycha'],
    'it': ['it', 'ita', 'italian', 'italyan', 'italiano', 'итальянский', 'italiya', 'italyancha'],
    'pt': ['pt', 'por', 'portuguese', 'portugal', 'português', 'portugues', 'португальский', 'portugalcha'],
    'hi': ['hi', 'hin', 'hindi', 'hind', 'हिन्दी', 'хинди', 'hindiston', 'hindcha'],
    'pl': ['pl', 'pol', 'polish', 'polsha', 'polski', 'польский', 'polcha'],
    'uk': ['uk', 'ukr', 'ukrainian', 'ukraina', 'українська', 'украинский', 'ukrain'],
    'nl': ['nl', 'dut', 'dutch', 'golland', 'nederlands', 'голландский', 'niderland'],
    'sv': ['sv', 'swe', 'swedish', 'shved', 'svenska', 'шведский', 'shvetsiya'],
    'cs': ['cs', 'cze', 'czech', 'chex', 'čeština', 'чешский', 'chexiya'],
    'el': ['el', 'gre', 'greek', 'yunon', 'ελληνικά', 'греческий', 'gretsiya'],
    'he': ['he', 'heb', 'hebrew', 'ibroniy', 'עברית', 'иврит', 'yahudiy'],
    'th': ['th', 'tha', 'thai', 'tailand', 'ไทย', 'тайский', 'taycha'],
    'vi': ['vi', 'vie', 'vietnamese', 'vyetnam', 'tiếng việt', 'вьетнамский', 'vyetnamcha'],
    'id': ['id', 'ind', 'indonesian', 'indoneziya', 'bahasa indonesia', 'индонезийский', 'indonez'],
    'fa': ['fa', 'per', 'persian', 'fors', 'فارسی', 'персидский', 'eron', 'forscha'],
    'ro': ['ro', 'rum', 'romanian', 'rumin', 'română', 'румынский', 'ruminiya'],
    'hu': ['hu', 'hun', 'hungarian', 'venger', 'magyar', 'венгерский', 'vengriya'],
    'da': ['da', 'dan', 'danish', 'daniya', 'dansk', 'датский', 'daniyacha'],
    'fi': ['fi', 'fin', 'finnish', 'finlyandiya', 'suomi', 'финский', 'fincha'],
    'no': ['no', 'nor', 'norwegian', 'norvegiya', 'norsk', 'норвежский', 'norvegcha'],
}

# Tillarning to'liq nomlari emoji bilan
LANGUAGE_NAMES = {
    'ru': '🇷🇺 Rus tili',
    'en': '🇬🇧 Ingliz tili',
    'uz': '🇺🇿 O\'zbek tili',
    'tr': '🇹🇷 Turk tili',
    'de': '🇩🇪 Nemis tili',
    'fr': '🇫🇷 Fransuz tili',
    'es': '🇪🇸 Ispan tili',
    'ar': '🇸🇦 Arab tili',
    'zh': '🇨🇳 Xitoy tili',
    'ja': '🇯🇵 Yapon tili',
    'ko': '🇰🇷 Koreys tili',
    'it': '🇮🇹 Italyan tili',
    'pt': '🇵🇹 Portugal tili',
    'hi': '🇮🇳 Hind tili',
    'pl': '🇵🇱 Polsha tili',
    'uk': '🇺🇦 Ukraina tili',
    'nl': '🇳🇱 Golland tili',
    'sv': '🇸🇪 Shved tili',
    'cs': '🇨🇿 Chex tili',
    'el': '🇬🇷 Yunon tili',
    'he': '🇮🇱 Ibroniy tili',
    'th': '🇹🇭 Tailand tili',
    'vi': '🇻🇳 Vyetnam tili',
    'id': '🇮🇩 Indoneziya tili',
    'fa': '🇮🇷 Fors tili',
    'ro': '🇷🇴 Rumin tili',
    'hu': '🇭🇺 Venger tili',
    'da': '🇩🇰 Daniya tili',
    'fi': '🇫🇮 Finlyandiya tili',
    'no': '🇳🇴 Norvegiya tili',
}


def detect_language_code(text: str) -> str:
    """Matndan til kodini aniqlaydi"""
    text_lower = text.lower().strip()
    
    for lang_code, variants in LANGUAGE_VARIANTS.items():
        for variant in variants:
            if text_lower == variant or text_lower.startswith(variant + ' '):
                return lang_code
    
    return None


def parse_query(query: str) -> tuple:
    """Query ni parse qiladi va til + matnni qaytaradi"""
    parts = query.strip().split(maxsplit=1)
    
    if len(parts) == 0:
        return None, None
    
    if len(parts) == 1:
        # Faqat matn kiritilgan, ingliz tiliga tarjima
        return 'en', parts[0]
    
    # Birinchi qismni til sifatida tekshirish
    lang_code = detect_language_code(parts[0])
    
    if lang_code and len(parts) > 1:
        return lang_code, parts[1]
    else:
        # Til topilmasa, butun matnni ingliz tiliga tarjima
        return 'en', query


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    help_text = """
🌍 <b>Tarjima Bot - Inline Translation Bot</b>

Bu bot har qanday chatda inline rejimda ishlaydi va matnni 30+ tilga tarjima qiladi!

<b>📝 Qanday ishlatish:</b>

1️⃣ Har qanday chatda bot nomini yozing:
   <code>@your_bot_name</code>

2️⃣ Til kodini va matnni kiriting:
   <code>@your_bot_name ru Salom</code>
   <code>@your_bot_name en Привет</code>
   <code>@your_bot_name uz Hello</code>

3️⃣ Variantlardan birini tanlang va yuboring!

<b>🌐 Til kodlari (har xil variantlarda):</b>

🇬🇧 <b>Ingliz:</b> en, eng, english, ingliz
🇷🇺 <b>Rus:</b> ru, rus, russian, русский
🇺🇿 <b>O'zbek:</b> uz, uzbek, o'zbek, ozbek
🇹🇷 <b>Turk:</b> tr, turk, turkish, türkçe
🇩🇪 <b>Nemis:</b> de, german, deutsch
🇫🇷 <b>Fransuz:</b> fr, french, français
🇪🇸 <b>Ispan:</b> es, spanish, español
🇸🇦 <b>Arab:</b> ar, arabic, عربي
🇨🇳 <b>Xitoy:</b> zh, chinese, 中文
🇯🇵 <b>Yapon:</b> ja, japanese, 日本語
🇰🇷 <b>Koreys:</b> ko, korean, 한국어
🇮🇹 <b>Italyan:</b> it, italian, italiano
🇵🇹 <b>Portugal:</b> pt, portuguese
🇮🇳 <b>Hind:</b> hi, hindi, हिन्दी

<b>💡 Misollar:</b>
• <code>@your_bot_name ru Salom do'stim</code> → Здравствуй мой друг
• <code>@your_bot_name english Привет</code> → Hello
• <code>@your_bot_name türkçe Hello world</code> → Merhaba dünya

<b>⚡ Tez tarjima:</b>
Agar til kodini yozmasangiz, matn avtomatik ingliz tiliga tarjima qilinadi.

<i>Botdan foydalanish uchun uni inline rejimga ulang!</i>
"""
    await update.message.reply_text(help_text, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help komandasi"""
    await start(update, context)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline query handler"""
    query = update.inline_query.query
    
    if not query or len(query.strip()) == 0:
        # Bo'sh query uchun yo'riqnoma
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="📖 Qanday ishlatish",
                description="Til kodini va matnni kiriting. Masalan: ru Salom",
                input_message_content=InputTextMessageContent(
                    "Botdan foydalanish:\n\n"
                    "1. Bot nomini yozing\n"
                    "2. Til kodini kiriting (ru, en, uz, va h.k.)\n"
                    "3. Tarjima qilmoqchi bo'lgan matnni yozing\n\n"
                    "Misol: @your_bot_name ru Salom → Здравствуйте"
                ),
                thumb_url="https://img.icons8.com/color/96/000000/translate.png"
            )
        ]
        await update.inline_query.answer(results, cache_time=0)
        return
    
    # Query ni parse qilish
    target_lang, text = parse_query(query)
    
    if not text:
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="❌ Matn kiritilmagan",
                description="Til va matnni kiriting",
                input_message_content=InputTextMessageContent("Matn kiritilmadi")
            )
        ]
        await update.inline_query.answer(results, cache_time=0)
        return
    
    results = []
    
    try:
        # Asosiy tilga tarjima
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        
        # Asosiy natija
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{LANGUAGE_NAMES.get(target_lang, target_lang.upper())} ✅",
                description=translated_text[:100],
                input_message_content=InputTextMessageContent(translated_text),
                thumb_url="https://img.icons8.com/color/96/000000/check.png"
            )
        )
        
        # Qo'shimcha tillar (eng mashhur)
        additional_langs = []
        if target_lang != 'en':
            additional_langs.append('en')
        if target_lang != 'ru':
            additional_langs.append('ru')
        if target_lang != 'uz':
            additional_langs.append('uz')
        if target_lang != 'tr':
            additional_langs.append('tr')
        if target_lang != 'de':
            additional_langs.append('de')
        if target_lang != 'fr':
            additional_langs.append('fr')
        
        # Qo'shimcha tarjimalar
        for lang in additional_langs[:5]:  # Faqat 5 ta qo'shimcha
            try:
                extra_translated = GoogleTranslator(source='auto', target=lang).translate(text)
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid.uuid4()),
                        title=f"{LANGUAGE_NAMES.get(lang, lang.upper())}",
                        description=extra_translated[:100],
                        input_message_content=InputTextMessageContent(extra_translated),
                        thumb_url="https://img.icons8.com/color/96/000000/language.png"
                    )
                )
            except Exception as e:
                logger.error(f"Qo'shimcha tarjima xatosi ({lang}): {e}")
        
        # Asl matn + tarjima
        combined = f"{text}\n\n{translated_text}"
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="📋 Asl matn + Tarjima",
                description=f"{text[:50]} → {translated_text[:50]}",
                input_message_content=InputTextMessageContent(combined),
                thumb_url="https://img.icons8.com/color/96/000000/copy.png"
            )
        )
        
    except Exception as e:
        logger.error(f"Tarjima xatosi: {e}")
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="❌ Tarjima xatosi",
                description="Qayta urinib ko'ring",
                input_message_content=InputTextMessageContent(
                    "Tarjima qilishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
                )
            )
        ]
    
    await update.inline_query.answer(results, cache_time=0)


def main():
    """Botni ishga tushirish"""
    # TOKENni environment variable'dan olish
    TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    if TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("⚠️  Xato: BOT_TOKEN environment variable o'rnatilmagan!")
        print("💡 Yo'riqnoma:")
        print("   Linux/Mac: export BOT_TOKEN='your_token_here'")
        print("   Windows: set BOT_TOKEN=your_token_here")
        print("   Yoki kodda to'g'ridan-to'g'ri TOKEN o'rnating")
        return
    
    # Flask serverni alohida thread'da ishga tushirish
    logger.info("🚀 Flask server ishga tushirilmoqda...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Application yaratish
    application = Application.builder().token(TOKEN).build()
    
    # Handlerlar qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(InlineQueryHandler(inline_query))
    
    # Botni ishga tushirish
    logger.info("🤖 Telegram bot ishga tushdi...")
    logger.info("✅ Bot inline rejimda ishlayapti!")
    logger.info("🌐 Health check: /health endpoint")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
