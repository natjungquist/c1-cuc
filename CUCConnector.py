# CUCConnector
# class that makes API requests to CUC

import zipfile
import os
import requests
import json
from CallHandler import CallHandler

class CUCConnector:

    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.call_handler_template_id = ""

    def get_template_id(self):
        url = f"https://{self.server}/vmrest/callhandlerprimarytemplates"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.get(
            url, 
            headers=headers, 
            auth = (self.username, self.password),
            verify=False
        )

        if response.status_code == 200: 
            print(f"Successfully received template object id")
            self.set_template_id(response.text)
            
        else:
            print(f"Failed to get template object id: {response.status_code} - {response.text}")

    def set_template_id(self, response_text):
        data = json.loads(response_text)
        self.call_handler_template_id = data["CallhandlerPrimaryTemplate"]["ObjectId"]
        print(self.call_handler_template_id)

    def create_handler_and_get_id(self, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers?templateObjectId={self.call_handler_template_id}"

        payload = json.dumps({
            "DisplayName": handler.get_name()
        })
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            url, 
            headers=headers, 
            auth = (self.username, self.password),
            data=payload,
            verify=False
        )

        if response.status_code == 201: 
            print(f"Call handler created: {response.text}")
            parts = response.text.split('/')
            handler.UnityId = parts[-1]
        else:
            print(f"Failed to create call handler: {response.status_code} - {response.text}")
    
    def set_dtmf_mapping(self, key, transfer_number, handler:CallHandler):
        pass
    
    def set_transfer_rule(self, handler:CallHandler):
        pass
    
    def set_pilot_identifier(self, handler:CallHandler):
        pass

    def set_schedule(self, handler:CallHandler):
        pass

    def upload_greeting(self, file_path, handler:CallHandler):
        id = handler.get_id()
        url = f"{self.server}/vmrest/handlers/callhandlers/{id}/greetings/Standard/greetingstreamfiles/1033/audio"
        headers = {
            "Content-Type":"audio/wav",
            "Accept":"application/json",
        }

        with open(file_path, "rb") as wav:
            response = requests.put(
                url,
                headers = headers,
                auth = (self.username, self.password),
                data = wav,
                verify=False
            )

        if response.status_code == 204:  # CUC API response has no content for this endpoint
            print(f"Uploaded {file_path} successfully")
        else:
            print(f"Failed to upload {file_path}: {response.status_code} - {response.text}")