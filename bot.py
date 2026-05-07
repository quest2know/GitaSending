import os
import datetime
import pytz
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import state
import drive_api

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data = state.get_user(chat_id)
    
    schedule_daily_job(context.job_queue, chat_id, user_data["alert_time"], user_data["timezone"])

    await update.message.reply_text(
        f"Hari Om! You are now registered to receive daily Gita audio files.\n"
        f"Your current alert time is {user_data['alert_time']} in timezone {user_data['timezone']}.\n"
        f"To change time: /settime HH:MM (e.g., /settime 06:00)\n"
        f"To change timezone: /settimezone Region/City (e.g., /settimezone America/New_York)\n"
        f"Use /sendnow to receive the next file immediately."
    )

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Please provide a time in HH:MM format. Example: /settime 06:00")
        return

    time_str = context.args[0]
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
        state.update_user(chat_id, alert_time=time_str)
        
        user_data = state.get_user(chat_id)
        schedule_daily_job(context.job_queue, chat_id, time_str, user_data["timezone"])
        
        await update.message.reply_text(f"Successfully updated your daily alert time to {time_str}.")
    except ValueError:
        await update.message.reply_text("Invalid time format. Please use HH:MM (e.g., /settime 06:00)")

async def settimezone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Please provide a valid timezone. Example: /settimezone Asia/Kolkata")
        return

    tz_str = context.args[0]
    if tz_str not in pytz.all_timezones:
        await update.message.reply_text("Invalid timezone. Please use a valid TZ identifier (e.g., America/New_York, Europe/London, Asia/Kolkata).")
        return

    state.update_user(chat_id, timezone=tz_str)
    
    user_data = state.get_user(chat_id)
    schedule_daily_job(context.job_queue, chat_id, user_data["alert_time"], tz_str)
    
    await update.message.reply_text(f"Successfully updated your timezone to {tz_str}.")

async def send_next_file_job(context: ContextTypes.DEFAULT_TYPE):
    """Job trigger that receives chat_id from job.data"""
    chat_id = context.job.data
    await dispatch_file(context.bot, chat_id)

async def sendnow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await dispatch_file(context.bot, chat_id)

async def dispatch_file(bot, chat_id):
    """Core function to fetch and send the file to a specific chat_id."""
    await bot.send_message(chat_id=chat_id, text="Fetching today's Gita audio...")

    try:
        if not DRIVE_FOLDER_ID:
            await bot.send_message(chat_id=chat_id, text="Error: DRIVE_FOLDER_ID is not set in .env")
            return

        mp3_files = drive_api.get_all_curriculum_files(DRIVE_FOLDER_ID)
        
        if not mp3_files:
            await bot.send_message(chat_id=chat_id, text="No MP3 files found matching CH* in the specified Google Drive subfolders.")
            return

        user_data = state.get_user(chat_id)
        last_index = user_data["last_file_index"]
        next_index = last_index + 1

        if next_index >= len(mp3_files):
            await bot.send_message(chat_id=chat_id, text="You have received all available files! Starting over from the beginning.")
            next_index = 0

        next_file = mp3_files[next_index]
        file_id = next_file['id']
        file_name = next_file['name']

        temp_path = f"temp_{file_name}"
        drive_api.download_file(file_id, temp_path)

        with open(temp_path, 'rb') as audio_file:
            await bot.send_audio(chat_id=chat_id, audio=audio_file, title=file_name)

        os.remove(temp_path)
        state.update_user(chat_id, last_file_index=next_index)

    except Exception as e:
        logger.error(f"Error sending file to {chat_id}: {e}")
        await bot.send_message(chat_id=chat_id, text=f"An error occurred while fetching the file: {str(e)}")

def schedule_daily_job(job_queue, chat_id, time_str, tz_str):
    """Schedules the daily job for a specific user."""
    job_name = f'daily_gita_job_{chat_id}'
    current_jobs = job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()

    hour, minute = map(int, time_str.split(':'))
    tz = pytz.timezone(tz_str)
    t = datetime.time(hour=hour, minute=minute, tzinfo=tz)
    
    job_queue.run_daily(send_next_file_job, time=t, data=chat_id, name=job_name)
    logger.info(f"Scheduled job for {chat_id} at {time_str} {tz_str}.")

def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is missing. Please add it to your .env file.")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settime", settime))
    application.add_handler(CommandHandler("settimezone", settimezone))
    application.add_handler(CommandHandler("sendnow", sendnow_command))

    print("Bot is starting... (Press Ctrl+C to stop)")
    
    # Reschedule all existing users
    all_users = state.get_all_users()
    for chat_str, user_data in all_users.items():
        schedule_daily_job(application.job_queue, chat_str, user_data["alert_time"], user_data["timezone"])

    application.run_polling()
