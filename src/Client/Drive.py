import os, io, json
from typing import Any
from googleapiclient.discovery import build, mimetypes
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaIoBaseDownload

FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

class Drive:
    
    @staticmethod
    def _print_all_drive_items(service: Any):
        response = service.files().list(spaces="drive", fields="files(id, name, mimeType, parents)").execute()
        print(json.dumps(response, indent=2))

    @staticmethod
    def get_drive_service():
        SCOPES = ['https://www.googleapis.com/auth/drive']
        KEY_FILE_LOCATION = os.path.join(os.environ["workspace"], "tokens", "google_drive_credentials.json")
        if not os.path.isfile(KEY_FILE_LOCATION):
            raise Exception(f"Please download the service account (credential) keys file from Google Cloud Console and place it in {KEY_FILE_LOCATION}")

        # Any is returned from build (it is constructed dynamically), so no intellisense here big man.
        # See https://developers.google.com/drive/api/v3/reference/files
        creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)
        return build("drive", "v3", credentials=creds)

    @staticmethod
    def download_latest_model(model_filepath: str):
        """
        model_filepath: Where to donwload the model tar file to
        """
        service = Drive.get_drive_service()
        tar_mime = mimetypes.guess_type("x.tar")[0]

        model_folder_name = "models"
        model_folder_id = service.files().list(spaces="drive", fields="files(id, name, modifiedTime)", q=f"'root' in parents and mimeType = '{FOLDER_MIME_TYPE}' and name = '{model_folder_name}'").execute().get("files", [])[0].get("id")
        model_files = service.files().list(spaces="drive", fields="files(id, name, modifiedTime)", q=f"'{model_folder_id}' in parents and mimeType = '{tar_mime}'", orderBy="modifiedTime desc").execute().get("files", [])
        newest_file_id = model_files[0].get("id")
        request = service.files().get_media(fileId=newest_file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        
        fh.seek(0)
        with open(model_filepath, "wb") as file:
            file.write(fh.read())