import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

import state

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captures the Chat ID, adds it to state.json, and confirms to the user."""
    chat = update.effective_chat
    user = update.effective_user
    
    # Try to add the ID to state
    is_new = state.add_chat_id(chat.id)
    
    print("\n" + "="*40)
    if is_new:
        print(f"NEW USER REGISTERED: {user.full_name} ({chat.id})")
        reply_text = "Namaste! You have been registered for the Daily Gita Dispatch. You will receive your first message during the next scheduled broadcast."
    else:
        print(f"MESSAGE FROM EXISTING USER: {user.full_name} ({chat.id})")
        reply_text = "You are already registered! You will continue to receive the daily recordings."
    
    print("="*40)
    
    try:
        await update.message.reply_text(reply_text)
    except Exception as e:
        print(f"Error sending reply to {chat.id}: {e}")

async def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file.")
        return

    print("Starting Automated Registration Bot...")
    print("Users can now join by sending any message to the bot.")
    print("Press Ctrl+C to stop and save all changes.")
    
    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    
    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping bot...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
