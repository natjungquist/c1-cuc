# TODO (WIP)
# CUCConnector
# class that makes API requests to CUC

import zipfile
import os
import requests

class CUCConnector:

    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password

    # WIP TESTING: does uploading an audio file work?
    def upload_greeting(self, path, extract_dir, handler_id):
        url = f"{self.server}/vmrest/handlers/callhandlers/{handler_id}/greetings/Alternate/greetingstreamfiles/1033/audio"
        headers = {
            "Content-Type":"audio/wav",
            "Accept":"application/json",
        }

        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        for filename in os.listdir(extract_dir):
            if filename.endswith(".wav"):
                file_path = os.path.join(extract_dir, filename)

            with open(file_path, "rb") as wav:
                response = requests.put(
                    url,
                    headers = headers,
                    auth = (self.username, self.password),
                    data = wav,
                    verify=False
                )
    
            if response.status_code == 204:  # CUC API response has no content for this endpoint
                print(f"Uploaded {filename} successfully")
            else:
                print(f"Failed to upload {filename}: {response.status_code} - {response.text}")