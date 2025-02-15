from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from django.core.files.storage import default_storage

# Path to your credentials JSON file
SERVICE_ACCOUNT_FILE = "core/cred.json"

# Authenticate with Google Drive API
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)


def upload_to_drive(file_path, file_name, folder_id=None):
    """Uploads a file to Google Drive and returns its URL."""
    file_metadata = {"name": file_name}

    # If you want to store in a specific folder
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()

    file_id = file.get("id")

    # Make the file publicly accessible (Optional)
    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"}
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"  # Public URL of the file



def save_file_in_local(attachment):
    file_url = None

    if attachment:
        file_name = default_storage.save(f"temp/{attachment.name}", attachment)
        file_path = default_storage.path(file_name)  # Get absolute path
        file_url = upload_to_drive(file_path, attachment.name)
        os.remove(file_path)  # Cleanup

    return file_url
