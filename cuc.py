import pandas as pd
import json

with open('config.json') as config_file:
    config = json.load(config_file)

CALLER_INPUT_FILE = config["callerInput"]["file"]
CALLER_INPUT_COLS = config["callerInput"]["columns"]
SCHEDULES_CONFIG_FILE = config["schedules"]["file"]
SCHEDULES_COLS = config["schedules"]["columns"]

caller_input_data = pd.read_csv(CALLER_INPUT_FILE, usecols=CALLER_INPUT_COLS)

# class AutoAttendant: self.name self.CUC_id self.caller_input
# class CUCAutoAttendantProvisioner
# interface CUCConnector
# save all the auto attendant names
# identify the auto attendants that need to be made first

# create them
# save their ids

# set their caller input

# ...

import zipfile
import os
import requests

class CUCConnector:

    def __init__(self):
        self.server = "https://10.0.0.64"
        self.username = ""
        self.password = ""

    def upload_greeting(self):
        handler_id = "ef98b1b5-4b17-4685-a459-c863ba9640da"
        url = f"{self.server}/vmrest/handlers/callhandlers/{handler_id}/greetings/Alternate/greetingstreamfiles/1033/audio"
        headers = {
            "Content-Type":"audio/wav",
            "Accept":"application/json",
        }

        path = "./tmp.zip"

        with zipfile.ZipFile(path, 'r') as zip_ref:
            extract_dir = "temp_wav_files"
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

if __name__ == "__main__":

    cuc = CUCConnector()
    cuc.upload_greeting()
    