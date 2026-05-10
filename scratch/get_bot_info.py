import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

async def get_bot_info():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("No token found")
        return
    
    bot = Bot(token=token)
    me = await bot.get_me()
    print(f"Bot Name: {me.first_name}")
    print(f"Bot Username: @{me.username}")

if __name__ == "__main__":
    asyncio.run(get_bot_info())
