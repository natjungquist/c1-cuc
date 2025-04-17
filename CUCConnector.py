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

    """
    gets the template id for call handlers at this server. 
    the template id is needed for requests to create new call handlers.
    """
    def get_template_id(self):
        url = f"https://{self.server}/vmrest/callhandlerprimarytemplates"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers, auth = (self.username, self.password),
            verify=False
        )

        if response.status_code == 200: 
            print(f"Received template object id\n")
            self.set_template_id(response.text)
            
        else:
            print(f"Failed to get template object id: {response.status_code} - {response.text}")

    """
    sets template id of call handler objects at this server. 
    """
    def set_template_id(self, response_text):
        data = json.loads(response_text)
        self.call_handler_template_id = data["CallhandlerPrimaryTemplate"]["ObjectId"]
        # print(self.call_handler_template_id)

    """
    creates a standard call handler with no settings besides its name.
    handler object must already have a name. 
    records the new handler's id and saves it to the handler object.
    """
    def create_handler_and_get_id(self, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers?templateObjectId={self.call_handler_template_id}"

        payload = json.dumps({
            "DisplayName": handler.get_name()
        })
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, auth = (self.username, self.password),
                                 data=payload,verify=False)

        if response.status_code == 201: 
            print(f"Call handler '{handler.get_name()}' created: {response.text}")
            parts = response.text.split('/')
            handler.UnityId = parts[-1]
        else:
            print(f"Failed to create call handler: {response.status_code} - {response.text}\n")
    
    """
    sets one key of a specified call handler to go to either a specified number or another call handler.
    transfer_to must be:
    (1) a string of digits representing a phone number or 
    (2) a string representing another existing handler's id.

    the Cisco Unity Connection (CUC) API cannot set a DTMF menu entry (i.e., key press in a call handler greeting) to play a specific WAV file directly. DTMF entries can only route to:
    - Users
    - Call handlers
    - Directory handlers
    - Interview handlers

    """
    def set_dtmf_mapping(self, key, transfer_to, handler:CallHandler, is_to_number):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/menuentries/{key}"

        if is_to_number:
          payload = f"<MenuEntry>\r\n    <Action>7</Action>\r\n    <TransferNumber>{transfer_to}</TransferNumber>\r\n</MenuEntry>"
        else:
          payload = f"<MenuEntry>\r\n<Action>2</Action>\r\n<TargetConversation>PHTransfer</TargetConversation>\r\n<TargetHandlerObjectId>{transfer_to}</TargetHandlerObjectId>\r\n</MenuEntry>"

        headers = {
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        }

        response = requests.put(url, headers=headers, auth = (self.username, self.password),
            data=payload, verify=False
        )

        if response.status_code == 204: 
            print(f"Call handler dtmf mapping set for handler {handler.get_name()} with key: {key} and mapping: {transfer_to}\n")
        else:
            print(f"Failed to set dtmf for handler {handler.get_name()} with key: {key} and mapping: {transfer_to}: {response.status_code} - {response.text}\n")
    
    """
    sets a standard transfer rule for a specified call handler.
    """
    def set_transfer_rule(self, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/transferoptions/Standard"

        payload = json.dumps({
            "Action": "1",
            "Extension": handler.transfer_rule_extension,
            "TransferType": "0",
            "Enabled": "true"
        })
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.put(url, headers=headers, auth = (self.username, self.password),
            data=payload, verify=False
        )

        if response.status_code == 204: 
            print(f"Transfer rule set for handler {handler.get_name()}\n")
        else:
            print(f"Failed to set transfer rule for handler {handler.get_name()}: {response.status_code} - {response.text}\n")

    """
    uploads an audio file to be the standard greeting of a call handler.
    file_path specifies the absolute path to the audio file. 
    audio file must be RIFF (little-endian) data, WAVE audio, PCM, 16 bit, mono 8000 Hz.
    """
    def upload_greeting(self, file_path, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/greetings/Standard/greetingstreamfiles/1033/audio"
        headers = {
            "Content-Type":"audio/wav",
            "Accept":"application/json",
        }

        with open(file_path, "rb") as wav:
            response = requests.put(url, headers = headers, auth = (self.username, self.password),
                data = wav, verify=False
            )

        if response.status_code == 204:
            print(f"Uploaded {file_path} for handler {handler.get_name()}\n")
        else:
            print(f"Failed to upload {file_path} for handler {handler.get_name()}: {response.status_code} - {response.text}\n")

    """
    sets the dmfm access id for a specified call handler.
    the handler object must already contain a pilot identifer number.
    equivalent to the pilot identifier in exchange UM.
    """
    def set_dtmf_access_id(self, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/"
        payload = f"<CallHandler>\r\n    <DTMFAccessId>{handler.PilotIdentifierList}</DTMFAccessId>\r\n    </CallHander>"
        headers = {
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        }

        response = requests.put(url, headers=headers, auth = (self.username, self.password),
            data=payload, verify=False
        )

        if response.status_code == 204: 
            print(f"Call handler {handler.get_name()} DTMFAccessId set with {handler.PilotIdentifierList}\n")
        else:
            print(f"Failed to set DTMFAccessId for {handler.get_name()}: {response.status_code} - {response.text}\n")
    

    """
    """
    def set_schedule(self, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/"
        pass