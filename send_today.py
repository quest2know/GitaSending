import os
import asyncio
import logging
from dotenv import load_dotenv
import telegram

import state
import drive_api

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def send_daily_gita():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    folder_id = os.getenv("DRIVE_FOLDER_ID")
    
    chat_id = state.get_target_chat_id()
    
    if not token or not folder_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or DRIVE_FOLDER_ID in environment.")
        return
        
    if not chat_id:
        logger.error("Target Chat ID is not set. Run 'python manage_state.py --set-chat-id <ID>' first.")
        return
        
    logger.info("Connecting to Google Drive to fetch the curriculum...")
    all_files = drive_api.get_all_curriculum_files(folder_id)
    
    if not all_files:
        logger.error("No valid audio files found in the Drive.")
        return
        
    last_index = state.get_last_file_index()
    next_index = last_index + 1
    
    if next_index >= len(all_files):
        logger.info("Curriculum completed! No more files to send.")
        bot = telegram.Bot(token=token)
        await bot.send_message(chat_id=chat_id, text="Congratulations! The entire Gita curriculum has been completed.")
        return
        
    next_file = all_files[next_index]
    logger.info(f"Downloading next file: {next_file['name']}")
    
    temp_path = f"temp_{next_file['name']}"
    try:
        drive_api.download_file(next_file['id'], temp_path)
        
        logger.info(f"Uploading {next_file['name']} to Telegram...")
        bot = telegram.Bot(token=token)
        
        with open(temp_path, 'rb') as audio_file:
            await bot.send_audio(
                chat_id=chat_id, 
                audio=audio_file, 
                title=next_file['name'],
                caption=f"Here is your daily recording: {next_file['name']}"
            )
            
        # Successfully sent, update state
        state.set_last_file_index(next_index)
        logger.info(f"Successfully sent {next_file['name']} and updated state index to {next_index}.")
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    asyncio.run(send_daily_gita())
