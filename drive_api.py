import io
import os
import re
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_drive_service():
    """Authenticates and returns the Google Drive API service."""
    # Check if credentials are provided as an Environment Variable (for cloud deployment)
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    print("creds_json",creds_json)
    if creds_json:
        creds_info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    else:
        # Fallback to local file
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Missing {SERVICE_ACCOUNT_FILE} or GOOGLE_CREDENTIALS_JSON.")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
    service = build('drive', 'v3', credentials=creds)
    return service

def extract_numbers_for_sorting(filename):
    """
    Extracts all numbers from a filename to allow 'natural sorting'
    (e.g. CH2 before CH10). Returns a tuple of integers.
    """
    numbers = re.findall(r'\d+', filename)
    return tuple(int(n) for n in numbers)

def get_all_curriculum_files(parent_folder_id):
    """
    Fetches all matching chapter files from subfolders within the parent folder.
    It builds a master list of files sorted sequentially across all chapters.
    """
    # If the user pasted the full URL, extract just the ID
    if "drive.google.com/drive/folders/" in parent_folder_id:
        parent_folder_id = parent_folder_id.split("drive.google.com/drive/folders/")[-1].split("?")[0]
        
    service = get_drive_service()
    
    # 1. Get all subfolders in the main folder
    folder_query = f"'{parent_folder_id}' in parents and trashed = false and mimeType = 'application/vnd.google-apps.folder'"
    folder_results = service.files().list(
        q=folder_query, 
        fields="files(id, name)", 
        pageSize=1000,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True
    ).execute()
    subfolders = folder_results.get('files', [])
    
    all_files = []
    
    # 2. Iterate through each subfolder and get files
    for folder in subfolders:
        file_query = f"'{folder['id']}' in parents and trashed = false and mimeType != 'application/vnd.google-apps.folder'"
        file_results = service.files().list(
            q=file_query, 
            fields="files(id, name, mimeType)", 
            pageSize=1000,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True
        ).execute()
        files = file_results.get('files', [])
        
        # Filter for files that start with CH (case insensitive) and end with .mp3
        for f in files:
            name = f['name']
            if name.lower().endswith('.mp3') and name.lower().startswith('ch'):
                all_files.append(f)
                
    # 3. Sort all files naturally across all folders
    # This ensures CH1_... comes before CH2_... and CH2_... before CH10_...
    all_files.sort(key=lambda x: extract_numbers_for_sorting(x['name']))
    
    return all_files

def download_file(file_id, output_path):
    """
    Downloads a file from Google Drive by its ID to the local output_path.
    """
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)

    
    with open(output_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
    return output_path

def get_curriculum_text(parent_folder_id):
    """
    Finds a .txt file in the main folder and returns its content as a string.
    Returns None if no such file is found.
    """
    if "drive.google.com/drive/folders/" in parent_folder_id:
        parent_folder_id = parent_folder_id.split("drive.google.com/drive/folders/")[-1].split("?")[0]
        
    service = get_drive_service()
    
    file_query = f"'{parent_folder_id}' in parents and trashed = false and name contains '.txt'"
    file_results = service.files().list(
        q=file_query, 
        fields="files(id, name)", 
        pageSize=10,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True
    ).execute()
    files = file_results.get('files', [])
    
    txt_file = None
    for f in files:
        if f['name'].lower().endswith('.txt'):
            txt_file = f
            break
            
    if not txt_file:
        return None
        
    request = service.files().get_media(fileId=txt_file['id'], supportsAllDrives=True)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        
    return fh.getvalue().decode('utf-8')
