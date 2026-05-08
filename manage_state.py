import argparse
import os
from dotenv import load_dotenv
import state
import drive_api

load_dotenv()

def set_last_file(filename):
    print(f"Connecting to Google Drive to find index for '{filename}'...")
    folder_id = os.getenv("DRIVE_FOLDER_ID")
    if not folder_id:
        print("Error: DRIVE_FOLDER_ID not found in .env")
        return

    try:
        all_files = drive_api.get_all_curriculum_files(folder_id)
        
        for i, f in enumerate(all_files):
            if f['name'] == filename:
                state.set_last_file_index(i)
                print(f"Success! Set '{filename}' as the last sent file (Index: {i}).")
                print(f"Tomorrow morning, the bot will pick up the NEXT file (Index: {i+1}).")
                return
        
        print(f"Error: Could not find '{filename}' anywhere in your Google Drive folders.")
        print("Please check the exact filename (e.g. CH1_01.mp3) and try again.")
    except Exception as e:
        print(f"Error communicating with Google Drive: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage GitaSending State")
    parser.add_argument('--set-chat-id', type=str, help="Set the target Telegram Chat ID")
    parser.add_argument('--set-last-file', type=str, help="Set the exact name of the last file sent (e.g. CH1_01.mp3)")
    
    args = parser.parse_args()
    
    if args.set_chat_id:
        state.set_target_chat_id(args.set_chat_id)
        print(f"Successfully set target chat ID to: {args.set_chat_id}")
        
    if args.set_last_file:
        set_last_file(args.set_last_file)

    if not args.set_chat_id and not args.set_last_file:
        print("Current Configuration:")
        print(f"Target Chat ID: {state.get_target_chat_id()}")
        print(f"Last File Index: {state.get_last_file_index()}")

if __name__ == "__main__":
    main()
