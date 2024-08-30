from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path, file_name, folder_id=None):
    # Load the service account credentials
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = 'service-key-google-cloud.json'  # Update with your service account path

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the Drive service
    service = build('drive', 'v3', credentials=credentials)

    # Create a MediaFileUpload object
    media = MediaFileUpload(file_path, mimetype='application/pdf')

    # Create the file metadata
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    # Upload the file
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f'File Link: https://drive.google.com/file/d/{file.get("id")}')
    return file.get('id')
