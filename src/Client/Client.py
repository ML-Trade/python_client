import io
from typing import Any
import zmq
from . import Globals
from Connection import Connection, ConnectionType
from googleapiclient.discovery import build, mimetypes
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import json
import os

FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


class Client:
    def __init__(self):
        self.loop = False
        self.subscriber = Connection(ConnectionType.SUB, Globals.PUBLISHER_PORT)
        self.api = Connection(ConnectionType.REQ, Globals.API_PORT)

    @staticmethod
    def _print_all_drive_items(service: Any):
        response = service.files().list(spaces="drive", fields="files(id, name, mimeType, parents)").execute()
        print(json.dumps(response, indent=2))

    @staticmethod
    def _get_drive_service():
        SCOPES = ['https://www.googleapis.com/auth/drive']
        KEY_FILE_LOCATION = os.path.join(os.environ["workspace"], "tokens", "google_drive_credentials.json")
        if not os.path.isfile(KEY_FILE_LOCATION):
            raise Exception(f"Please download the service account (credential) keys file from Google Cloud Console and place it in {KEY_FILE_LOCATION}")

        # Any is returned from build (it is constructed dynamically), so no intellisense here big man.
        # See https://developers.google.com/drive/api/v3/reference/files
        creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)
        return build("drive", "v3", credentials=creds)

    def start(self):
        service = Client._get_drive_service()
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
        
        
        model_filepath = os.path.join(os.environ["workspace"], "current_model.tar")
        fh.seek(0)
        with open(model_filepath, "wb") as file:
            file.write(fh.read())

        # self.loop = True
        # while self.loop:
        #     # Now, we wait
        #     result = self.subscriber.recieve(no_wait=False)
        #     if result is None:
        #         print("Recieved invalid or no data")
        #         continue
        #     print(f"Putting {result} into model")
        #     print(f"Sending Trade to buy at market")
        #     buyOrder = {
        #         "action": "TRADE",
        #         "options": {
        #             "action": "BUY",
        #             "type": "MARKET",
        #             "amount": 0.01
        #         }
        #     }
        #     closeOrder = {
        #         "action": "TRADE",
        #         "options": {
        #             "action": "CLOSE",
        #             "ticket_id": 1,
        #         }
        #     }
        #     self.api.send(buyOrder)
        #     response = self.api.recieve(no_wait=False)
        #     ticket_id = response["ticket_id"]
        #     print(f"Ticket {ticket_id} created")
        #     # Get prediction
        #     # Send recommendation back to MQL