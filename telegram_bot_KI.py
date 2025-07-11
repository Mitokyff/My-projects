import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import asyncio
import os
import requests
import uuid

TELEGRAM_TOKEN = "your-telegram-bot-token"
GEMINI_API_KEY = "your-google-gemini-api-key"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
chat_session = model.start_chat(history=[])

MAX_MESSAGE_LENGTH = 4096

async def send_long_message(update: Update, text: str):
    if not text:
        return
    
    parts = []
    while len(text) > 0:
        if len(text) > MAX_MESSAGE_LENGTH:
            part = text[:MAX_MESSAGE_LENGTH]
            last_newline = part.rfind('\n')
            if last_newline != -1:
                part = text[:last_newline]
                text = text[last_newline+1:]
            else:
                text = text[MAX_MESSAGE_LENGTH:]
            parts.append(part)
        else:
            parts.append(text)
            break
            
    for part in parts:
        try:
            await update.message.reply_text(part)
        except Exception as e:
            print(f"Error sending message part: {e}")
        await asyncio.sleep(0.1)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = ""
    
    if update.message.voice:
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.constants.ChatAction.TYPING)
            voice_file = await context.bot.get_file(update.message.voice.file_id)
            file_name = f"{uuid.uuid4()}.ogg"
            await voice_file.download_to_drive(file_name)
            
            audio_file = genai.upload_file(path=file_name)

            response = model.generate_content([
                "Transcribe the spoken words in this audio verbatim. Do not translate. Provide only the transcribed text.", 
                audio_file
            ])
            
            os.remove(file_name)

            if response and response.text:
                user_message = response.text.strip()
            else:
                await update.message.reply_text("Sorry, I could not understand the audio.")
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.constants.ChatAction.TYPING)
                return

        except Exception as e:
            print(f"Error processing voice message: {e}")
            await update.message.reply_text("An error occurred while processing the voice message.")
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.constants.ChatAction.TYPING)
            return

    elif update.message.text:
        user_message = update.message.text

    if user_message:
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.constants.ChatAction.TYPING)
            response = chat_session.send_message(user_message)
            await send_long_message(update, response.text)
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.constants.ChatAction.TYPING)
        except Exception as e:
            print(f"Error generating response from Gemini: {e}")
            await update.message.reply_text("An error occurred while generating a response.")
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.constants.ChatAction.TYPING)

def main():
    print("Bot is starting...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
