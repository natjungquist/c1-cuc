# CUCConnector
# class that makes API requests to CUC

import requests
import json
from CallHandler import CallHandler
from util import _log_success, _log_error
from find_missing_wav_files import INVALID_OPTIONS

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
            _log_error(f"ERROR: failed to get template object id: {response.status_code} - {response.text}")

    """
    sets template id of call handler objects at this server. 
    """
    def set_template_id(self, response_text):
        data = json.loads(response_text)
        self.call_handler_template_id = data["CallhandlerPrimaryTemplate"][0]["ObjectId"] # the first template (index 0) listed is the SDUSD_Template defined already in CUC server

    """
    creates a standard call handler with no settings besides its name.
    handler object must already have a name. 
    records the new handler's id and saves it to the handler object.

    args:
        - handler: CallHandler object. Must have a defined Name.
    """
    def create_handler_and_get_id(self, handler:CallHandler):
        if not handler.Name:
            _log_error(f"ERROR: failed to create call handler because its name was not defined.")
            return

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
            _log_success(f"'{handler.Name}' created: {response.text}")
            parts = response.text.split('/')
            handler.UnityId = parts[-1]
        else:
            _log_error(f"ERROR: failed to create call handler: {response.status_code} - {response.text}")
    
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

    args:
        - handler: CallHandler object. Must have a defined ID.
        - key: string representing key to press.
        - transfer_to: string representing 9 digit number to transfer to or the id of another call handler.
        - is_to_number: boolean. True if this mapping goes to a number. False if it goes to another handler.
    """
    def set_dtmf_mapping(self, key, transfer_to, handler:CallHandler, is_to_number):
        if not handler.get_id() or handler.get_id() in INVALID_OPTIONS:
            _log_error(f"ERROR: cannot set DTMF mapping for '{handler.Name}' because handler's ID is not defined.")
            return
        if not key:
            _log_error(f"ERROR: cannot set DTMF mapping for '{handler.Name}' because key is not defined.")
            return
        if not transfer_to:
            _log_error(f"ERROR: cannot set DTMF mapping for '{handler.Name}' because value to map to on key {key} is not defined.")
            return

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
            _log_success(f"'{handler.Name}' set with key: {key} and mapping: {transfer_to}")
        else:
            _log_error(f"ERROR: failed to set dtmf for handler '{handler.Name}' with key: {key} and mapping: {transfer_to}: {response.status_code} - {response.text}")
    
    """
    sets a standard transfer rule for a specified call handler.

    args:
        - handler: CallHandler object. Must have a defined ID and transfer rule extension.
    """
    def set_standard_transfer_rule_to_extension(self, handler:CallHandler):
        if not handler.get_id() or handler.get_id() in INVALID_OPTIONS:
            _log_error(f"ERROR: cannot set standard transfer rule for '{handler.Name}' because handler's ID is not defined.")
            return
        if not handler.transfer_rule_extension:
            _log_error(f"ERROR: cannot set standard transfer rule for '{handler.Name}' because extension is not defined.")
            return

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
            _log_success(f"'{handler.Name}' transfer rule set to {handler.transfer_rule_extension}")
        else:
            _log_error(f"ERROR: failed to set transfer rule for handler '{handler.Name}': {response.status_code} - {response.text}")

    """
    uploads an audio file to be the greeting of a call handler.
    file_path specifies the absolute path to the audio file. 
    audio file must be RIFF (little-endian) data, WAVE audio, PCM, 16 bit, mono 8000 Hz.

    args:
        - handler: CallHandler object. Must have a defined ID.
        - greeting_type: a string 'Standard' or 'Closed'
    """
    def upload_greeting(self, file_path, handler:CallHandler, greeting_type):
        if not handler.get_id() or handler.get_id() in INVALID_OPTIONS:
            _log_error(f"ERROR: cannot upload {greeting_type} greeting for '{handler.Name}' because handler's ID is not defined.")
            return

        if greeting_type.lower() == 'closed':
            greeting_type = "Off%20Hours"

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
            _log_success(f"'{handler.Name}' greeting uploaded for {greeting_type}")
        else:
            _log_error(f"ERROR: failed to upload {file_path} for handler '{handler.Name}': {response.status_code} - {response.text}")

    """
    sets the dmfm access id for a specified call handler.
    the handler object must already contain a pilot identifer number.
    equivalent to the pilot identifier in exchange UM.

    args:
        - handler: CallHandler object. Must have a defined PilotIdentifierList.
    """
    def set_dtmf_access_id(self, handler:CallHandler):
        if not handler.PilotIdentifierList or handler.PilotIdentifierList in INVALID_OPTIONS:
            _log_error(f"ERROR: cannot set pilot identifier for '{handler.Name}' because it is not defined.")
            return

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
            _log_success(f"'{handler.Name}' DTMFAccessId set with {handler.PilotIdentifierList}")
        elif response.status_code == 400 and "Duplicate" in response.text:
            _log_error(f"ERROR: '{handler.Name}' DTMF access ID not set because another handler is already assigned to it.")
        else:
            _log_error(f"ERROR: failed to set DTMFAccessId for '{handler.Name}': {response.status_code} - {response.text}")
    

    """
    sets a handler's closed action to map to an existing call handler on timeout.
    """
    def set_closed_handler(self, closed_handler_id, handler:CallHandler):
        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/greetings/Off%20Hours"
        
        payload = f"<Greeting>\r\n<AfterGreetingAction>2</AfterGreetingAction>\r\n    <AfterGreetingTargetConversation>PHTransfer</AfterGreetingTargetConversation>\r\n    <AfterGreetingTargetHandlerObjectId>{closed_handler_id}</AfterGreetingTargetHandlerObjectId>\r\n</Greeting>"

        headers = {
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        }

        response = requests.put(url, headers=headers, auth = (self.username, self.password),
            data=payload, verify=False
        )

        if response.status_code == 204:
            _log_success(f"'{handler.Name}' closed handler set")
        else:
            _log_error(f"ERROR: failed to set closed handler for handler '{handler.Name}': {response.status_code} - {response.text}")

    """
    sets the after greeting action to go to 

    args:
        - handler: CallHandler object. Must have a defined ID.
    """
    def set_standard_after_greeting_action(self, handler:CallHandler):
        if not handler.get_id() or handler.get_id() in INVALID_OPTIONS:
            _log_error(f"ERROR: cannot set after greeting action for '{handler.Name}' because handler's ID is not defined.")
            return

        url = f"https://{self.server}/vmrest/handlers/callhandlers/{handler.get_id()}/greetings/Standard"
        headers = {
            "Content-Type":"application/json",
            "Accept":"application/json",
        }
        data = json.dumps({
            "AfterGreetingAction": "2",
            "AfterGreetingTargetHandlerObjectId": handler.get_id(),
            "AfterGreetingTargetConversation": "PHTransfer"
        })

        response = requests.put(url, headers = headers, auth = (self.username, self.password), data = data, verify=False)

        if response.status_code == 204:
            _log_success(f"'{handler.Name}' after greeting action set")
        else:
            _log_error(f"ERROR: failed to set after greeting action for handler '{handler.Name}': {response.status_code} - {response.text}")