from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import asyncio

TELEGRAM_TOKEN = "7463890992:AAGHWvIR-XzO-VCdBR5bEr-UbIY6XcKI30I"
GEMINI_API_KEY = "AIzaSyAnnsWGT0ykhKWAT9ryWN-esPhW-RMTYa8"

genai.configure(api_key=GEMINI_API_KEY)
model_name = "gemini-2.5-flash"

gemini_model = genai.GenerativeModel(model_name)

MAX_MESSAGE_LENGTH = 3900

async def send_long_message(update: Update, text: str):
    if not text:
        return

    if len(text) <= MAX_MESSAGE_LENGTH:
        try:
            await update.message.reply_text(text)
        except Exception as e:
            print(f"Ошибка при отправке короткого сообщения: {e}")
            await update.message.reply_text("Извините, произошла ошибка при отправке ответа.")
        return

    estimated_part_info_overhead = 20
    effective_chunk_content_length = MAX_MESSAGE_LENGTH - estimated_part_info_overhead

    if effective_chunk_content_length <= 0:
        effective_chunk_content_length = MAX_MESSAGE_LENGTH

    chunks = [text[i:i + effective_chunk_content_length] for i in range(0, len(text), effective_chunk_content_length)]

    total_chunks = len(chunks)
    for i, chunk in enumerate(chunks):
        part_info = f" (Часть {i+1}/{total_chunks})" if total_chunks > 1 else ""

        message_to_send = chunk + part_info

        if len(message_to_send) > MAX_MESSAGE_LENGTH:
            message_to_send = message_to_send[:MAX_MESSAGE_LENGTH]

        try:
            await update.message.reply_text(message_to_send)
        except Exception as e:
            print(f"Не удалось отправить часть сообщения. Ошибка: {e}")
            print(f"Длина проблемного сообщения: {len(message_to_send)}")
            print(f"Содержимое проблемного сообщения (первые 200 символов): {message_to_send[:200]}")
            await update.message.reply_text("Извините, ответ слишком длинный и не может быть отправлен целиком даже по частям. Пожалуйста, попробуйте более короткий запрос.")
            break

        await asyncio.sleep(0.5)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = gemini_model.generate_content(user_message)
        reply = response.text
    except Exception as e:
        reply = f"Ошибка при генерации ответа: {e}"
        print(f"Ошибка Gemini API: {e}")

    await send_long_message(update, reply)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
