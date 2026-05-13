import os
import re
import asyncio
import logging
from dotenv import load_dotenv
import telegram
from telegram.error import TelegramError

import state
import drive_api

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def send_daily_gita():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    folder_id = os.getenv("DRIVE_FOLDER_ID")
    
    chat_ids = state.get_chat_ids()
    
    if not token or not folder_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or DRIVE_FOLDER_ID in environment.")
        return
        
    if not chat_ids:
        logger.error("No Chat IDs are registered. Run 'python capture_id.py' to add users.")
        return
        
    logger.info("Connecting to Google Drive to fetch the curriculum...")
    all_files = drive_api.get_all_curriculum_files(folder_id)
    
    if not all_files:
        logger.error("No valid audio files found in the Drive.")
        return
        
    last_index = state.get_last_file_index()
    next_index = last_index + 1
    
    bot = telegram.Bot(token=token)
    
    if next_index >= len(all_files):
        logger.info("Curriculum completed! Sending completion message to all users.")
        for chat_id in chat_ids:
            try:
                await bot.send_message(chat_id=chat_id, text="Congratulations! The entire Gita curriculum has been completed.")
            except TelegramError as e:
                logger.error(f"Failed to send completion message to {chat_id}: {e}")
        return
        
    next_file = all_files[next_index]
    logger.info(f"Downloading next file: {next_file['name']}")
    
    temp_path = f"temp_{next_file['name']}"
    try:
        drive_api.download_file(next_file['id'], temp_path)
        
        # Fetch text content
        text_content = drive_api.get_curriculum_text(folder_id)
        text_message = None
        if text_content:
            text_parts = re.split(r'#{2,}', text_content)
            if next_index < len(text_parts):
                text_message = text_parts[next_index].strip()
            else:
                logger.warning(f"Text file does not have enough segments for index {next_index}")
        
        logger.info(f"Broadcasting {next_file['name']} to {len(chat_ids)} users...")
        
        for chat_id in chat_ids:
            try:
                with open(temp_path, 'rb') as audio_file:
                    # We need to seek(0) if we reuse the file handle, 
                    # but here we are opening it fresh each time or reading it once.
                    # Since we open it inside the loop, it's fresh.
                    await bot.send_audio(
                        chat_id=chat_id, 
                        audio=audio_file, 
                        title=next_file['name'],
                        caption=""
                    )
                
                if text_message:
                    await bot.send_message(chat_id=chat_id, text=text_message)
                    
                logger.info(f"Successfully sent to {chat_id}")
            except TelegramError as e:
                logger.error(f"Failed to send to {chat_id}: {e}")
            
        # Successfully attempted all, update state index
        state.set_last_file_index(next_index)
        logger.info(f"Broadcast complete. Updated state index to {next_index}.")
        
    except Exception as e:
        logger.error(f"Critical error during execution: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    asyncio.run(send_daily_gita())
