# CUCConnector
# class that makes API requests to CUC

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
            print(f"ERROR: failed to get template object id: {response.status_code} - {response.text}")

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
            "DisplayName": handler.Name
        })
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, auth = (self.username, self.password),
                                 data=payload,verify=False)

        if response.status_code == 201: 
            print(f"'{handler.Name}' created: {response.text}")
            parts = response.text.split('/')
            handler.UnityId = parts[-1]
        else:
            print(f"ERROR: failed to create call handler: {response.status_code} - {response.text}")
    
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
            print(f"{handler.Name} set with key: {key} and mapping: {transfer_to}")
        else:
            print(f"ERROR: failed to set dtmf for handler '{handler.Name}' with key: {key} and mapping: {transfer_to}: {response.status_code} - {response.text}")
    
    """
    sets a standard transfer rule for a specified call handler.
    """
    def set_standard_transfer_rule_to_extension(self, handler:CallHandler):
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
            print(f"{handler.Name} transfer rule set")
        else:
            print(f"ERROR: failed to set transfer rule for handler '{handler.Name}': {response.status_code} - {response.text}")

    """
    uploads an audio file to be the greeting of a call handler.
    file_path specifies the absolute path to the audio file. 
    audio file must be RIFF (little-endian) data, WAVE audio, PCM, 16 bit, mono 8000 Hz.

    args:
        greeting_type: a string 'Standard' or 'Closed'
    """
    def upload_greeting(self, file_path, handler:CallHandler, greeting_type):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/greetings/{greeting_type}/greetingstreamfiles/1033/audio"
        headers = {
            "Content-Type":"audio/wav",
            "Accept":"application/json",
        }

        with open(file_path, "rb") as wav:
            response = requests.put(url, headers = headers, auth = (self.username, self.password),
                data = wav, verify=False
            )

        if response.status_code == 204:
            print(f"'{handler.Name}' business hours main menu prompt uploaded")
        else:
            print(f"ERROR: failed to upload {file_path} for handler '{handler.Name}': {response.status_code} - {response.text}")

    """
    sets the dmfm access id for a specified call handler.
    the handler object must already contain a pilot identifer number.
    equivalent to the pilot identifier in exchange UM.
    """
    def set_dtmf_access_id(self, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}"
        payload =json.dumps({
            "DtmfAccessId": handler.PilotIdentifierList
        })
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.put(url, headers=headers, auth = (self.username, self.password),
            data=payload, verify=False
        ) 

        if response.status_code == 204: 
            print(f"{handler.Name} DTMFAccessId set with {handler.PilotIdentifierList}")
        elif response.status_code == 400 and "Duplicate" in response.text:
            print(f"ERROR: '{handler.Name}' DTMF access ID not set because another handler is already assigned to it.")
        else:
            print(f"ERROR: failed to set DTMFAccessId for '{handler.Name}': {response.status_code} - {response.text}")
    

    """
    enables the closed greeting with not end date.
    sets a handler's closed action to map to an existing call handler on timeout.
    """
    def set_closed_handler(self, closed_handler_id, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/greetings/Off%20Hours"
        
        payload = f"""<Greeting>\r\n    <Status>\r\n        <EndDateSelection>2</EndDateSelection>\r\n    </Status>\r\n     <AfterGreetingAction>2</AfterGreetingAction>\r\n        <AfterGreetingTargetConversation>PHTransfer</AfterGreetingTargetConversation>\r\n        <AfterGreetingTargetHandlerObjectId>{closed_handler_id}</AfterGreetingTargetHandlerObjectId>\r\n    \r\n\r\n</Greeting>
        """

        headers = {
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        }

        response = requests.put(url, headers=headers, auth = (self.username, self.password),
            data=payload, verify=False
        )

        if response.status_code == 204:
            print(f"'{handler.Name}' closed handler set")
        else:
            print(f"ERROR: failed to set closed handler for handler '{handler.Name}': {response.status_code} - {response.text}")

    """
    """
    def set_schedule(self, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/"
        pass