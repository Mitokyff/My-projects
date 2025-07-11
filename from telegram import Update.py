from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

TELEGRAM_TOKEN = "your-telegram-bot-token"
GEMINI_API_KEY = "your-google-gemini-api-key"

genai.configure(api_key="GEMINI_API_KEY") # Используем переменную GEMINI_API_KEY здесь
model_name = "gemini-2.5-flash" # Названия моделей обычно не имеют префикса "models/" при инициализации

# Инициализируем модель глобально или внутри функции, если предпочтительнее,
# но инициализация один раз эффективнее для многократного использования.
gemini_model = genai.GenerativeModel(model_name)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        # Теперь вызываем метод generate_content на экземпляре модели
        response =  gemini_model.generate_content(user_message)
        reply = response.text
    except Exception as e:
        reply = f"Ошибка при генерации ответа: {e}"

    await update.message.reply_text(reply)

app = ApplicationBuilder().token("TELEGRAM_TOKEN").build() # Используем переменную TELEGRAM_TOKEN здесь
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
