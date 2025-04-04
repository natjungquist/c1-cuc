# CUCConnector
# class that makes API requests to CUC

import zipfile
import os
import requests
from AutoAttendant import AutoAttendant

class CUCConnector:

    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password

    def create_handler(self, name):
        pass
    
    # read the mappings from attendant and set them one by one??
    # or this function sets one mapping at a time, but attendant provisioner iterates over the mappings and calls this function over and over?
    def set_dtmf_mapping(self, attendant):
        pass
    
    def set_business_hours(self, attendant):
        pass
    
    def set_after_hours(self, attendant):
        pass

    # may need to be set for regular and after hours attendants???
    # WIP TESTING: does uploading an audio file work?
    def upload_greeting(self, path, extract_dir, attendant:AutoAttendant):
        id = attendant.get_id()
        url = f"{self.server}/vmrest/handlers/callhandlers/{id}/greetings/Alternate/greetingstreamfiles/1033/audio"
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