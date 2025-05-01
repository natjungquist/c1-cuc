# main

# python -m pip install pandas
# python -m pip install ffmpeg-python
  # download ffmpeg exe. 7zip to Program Files\ffmpeg add to system path. 
from CUCConnector import CUCConnector
from CallHandler import CallHandler
from find_missing_wav_files import get_audio_file_path, INVALID_OPTIONS
import pandas as pd
import json
import os
import urllib3
from util import _log_error, init_logs

PATH_TO_AUDIO_FILES = os.path.join(os.getcwd(), "converted_wav_files") 
    
"""
helper method get full 9 digit number because 
some handlers only specify a 4 digit extension.
"""
def get_full_number(extension, handler:CallHandler):
  return '80' + handler.prefix + extension

"""
removes the '.wav' extension from the end of a string if present.

args:
  filename: The input string (filename).

returns:
  the string with '.wav' removed if it was present at the end, 
  otherwise the original string.
"""
def remove_wav(filename):
  if filename.lower().endswith(".wav"):
    return filename[:-4]
  else:
    return filename

"""
sets all mappings for one call handler.

specifications:
- handler.OperatorExtension means use key 0 for this number.
- handler.BusinessHoursKeyMapping holds the other keys to make mappings for.
- if customer data says a key is "-", interpret this as meaning timeout, aka transfer rule.
- if there is no dash transfer rule will be operator extension.
- if customer data says the transfer_to is to a .wav file, make a new handler for this to play that audio file as its greeting.
- all mappings must go to a 9 digit number or another call handler.
"""
def set_business_hours_keys_and_transfer_rules(handler:CallHandler, cn:CUCConnector, call_handlers):
  # operator mapping
  if handler.OperatorExtension and handler.OperatorExtension not in INVALID_OPTIONS and not pd.isna(handler.OperatorExtension):
    cn.set_dtmf_mapping("0", handler.OperatorExtension, handler, is_to_number=True)

  # other mappings
  mapping_list = handler.BusinessHoursKeyMapping.split(';')
  has_dash = False
  for mapping in mapping_list:
    mapping_parts = mapping.split(',')
    if len(mapping_parts) < 4:
      _log_error(f"ERROR: mapping parts invalid. Could not set business hours key mappings for '{handler.Name}'")

    transfer_to = None
    key = mapping_parts[0].strip()

    # option 1. go to a number
    if (mapping_parts[2] not in INVALID_OPTIONS):
      transfer_to = mapping_parts[2]
      if len(transfer_to) == 4: #only an extension was specified
        transfer_to = get_full_number(transfer_to, handler)

      #must be 9 digits long to proceed
      if len(transfer_to) == 9: 
        if key == '-': #dash from customer data represents timeout
          has_dash = True
          handler.set_transfer_rule_extension(transfer_to)
          cn.set_standard_transfer_rule_to_extension(handler)
        else: #not a dash, set mapping
          cn.set_dtmf_mapping(key, transfer_to, handler, is_to_number=True)
      else:
        _log_error(f"ERROR: could not make 9-digit key mapping for handler '{handler.Name}'\n")

    # option 2. go to another call handler that already exists
    elif (mapping_parts[3] not in INVALID_OPTIONS):
      transfer_to = mapping_parts[3]

      handler_next = call_handlers.get(transfer_to)
      if handler_next:
        handler_next_id = handler_next.get_id()
      else:
        handler_next_id = None

      if not handler_next_id:
        _log_error(f"ERROR: error getting id of handler to transfer to\n")
      else:
        cn.set_dtmf_mapping(key, transfer_to, handler, is_to_number=False)

   # option 3. create a new call handler to go to
    elif (mapping_parts[4] not in INVALID_OPTIONS): # go to a wav file
      transfer_to = mapping_parts[4]

      # create the new handler set its greeting to the name specified
      new_handler = CallHandler()
      new_handler.Name = remove_wav(transfer_to)
      cn.create_handler_and_get_id(new_handler) # create it
      call_handlers[new_handler.Name] = new_handler # add it to dictionary of all handlers
      
      audio_file_path = get_audio_file_path(transfer_to, PATH_TO_AUDIO_FILES)
      if audio_file_path:
        cn.upload_greeting(audio_file_path, new_handler, 'Standard')
      else:
        _log_error(f"ERROR: audio file {audio_file_path} not found\n")   

      # set this call handler to map to the new handler
      cn.set_dtmf_mapping(key, new_handler.get_id(), handler, is_to_number=False)
    
  # set the transfer rule to the OperatorExtension if there was not already one specified
  if not has_dash:
    if handler.OperatorExtension and handler.OperatorExtension not in INVALID_OPTIONS:
      handler.set_transfer_rule_extension(handler.OperatorExtension)
      cn.set_standard_transfer_rule_to_extension(handler)


"""
checks if the handler already exists.

returns:
  true of it already exists, false if not.
"""
def handler_exists(name, call_handlers):
  desired_handler = call_handlers.get(name)
  if desired_handler:
    return True
  return False

"""
assumptions:
- handler has AfterHoursKeyMapping
- the AfterHoursKeyMapping is formatted correctly
- the mapping has 1 value
- it is '-' going to another handler, referenced by its name
- the other handler already exists
"""
def set_after_hours_to_handler(handler:CallHandler, call_handlers, cn:CUCConnector):
  mapping_parts = handler.AfterHoursKeyMapping.split(',')
  if len(mapping_parts) < 3:
    _log_error(f"ERROR: mapping parts invalid for after hours key mapping on handler '{handler.Name}'")

  if mapping_parts[3] not in INVALID_OPTIONS:
    transfer_to = mapping_parts[3]

    handler_next = call_handlers.get(transfer_to)
    if handler_next:
      handler_next_id = handler_next.get_id()
    else:
      handler_next_id = None

    if not handler_next_id:
      _log_error(f"ERROR: error getting id of handler to transfer to for after hours on handler '{handler.Name}'\n")
    else:
      cn.set_closed_handler(handler_next_id, handler)

"""
assumptions:
- handler.AfterHoursMainMenuCustomPromptFilename has a .wav file specified
- no AfterHoursKeyMapping exists
- the .wav file exists
- 
"""
def set_closed_greeting(handler:CallHandler, cn:CUCConnector, audio_path_name):
  audio_file_path = get_audio_file_path(audio_path_name, PATH_TO_AUDIO_FILES)
  if audio_file_path:
    cn.upload_greeting(audio_file_path, handler, 'Closed')
  else:
    _log_error(f"ERROR: audio file {audio_file_path} not found\n")   

"""
assumptions:
- handler.AfterHoursWelcomeGreetingFilename has a .wav file specified. This file exists.
- AfterHoursKeyMapping specified.
- need to create a new handler for this .wav file and mappings.
- reuse the operator extension of handler for the new handler.
"""
def create_new_after_hours_handler(handler:CallHandler, cn:CUCConnector, call_handlers):
  name = remove_wav(handler.AfterHoursMainMenuCustomPromptFilename)
  new_handler = CallHandler()
  new_handler.Name = name
  new_handler.BusinessHoursKeyMapping = handler.AfterHoursKeyMapping
  if handler.OperatorExtension and handler.OperatorExtension not in INVALID_OPTIONS and not pd.isna(handler.OperatorExtension):
    new_handler.OperatorExtension = handler.OperatorExtension

  cn.create_handler_and_get_id(new_handler)
  call_handlers[new_handler.Name] = new_handler

  set_business_hours_keys_and_transfer_rules(new_handler, cn, call_handlers)  


def test():
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  # load in config items
  print("loading in config...\n")
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = "testclosed.csv"
  SERVER = config["server"]
  USERNAME = config["username"]
  PASSWORD = config["password"]
  cn = CUCConnector(SERVER, USERNAME, PASSWORD)
  cn.get_template_id()

  # set info for all handlers
  call_handlers = {} #key: name, value:handler

  df = pd.read_csv(FILE)

  print("creating handlers...\n")
  for index, row in df.iterrows():
      handler = CallHandler(row)
      cn.create_handler_and_get_id(handler) # create it
      call_handlers[handler.Name] = handler # add it to the dictionary of all handlers
  
  for handler in call_handlers.values():
    handler: CallHandler

    cn.enable_closed(handler)



def main():
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # set this because the server is an insecure IP not a regular domain

  # load in config items
  print("loading in config...\n")
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = config["autoAttendantsFile"]
  SERVER = config["server"]
  USERNAME = config["username"]
  PASSWORD = config["password"]
  cn = CUCConnector(SERVER, USERNAME, PASSWORD)
  cn.get_template_id()

  # set info for all handlers
  call_handlers = {} #key: name, value:handler

  df = pd.read_csv(FILE)

  print("creating handlers...\n")
  for index, row in df.iterrows():
      handler = CallHandler(row)
      cn.create_handler_and_get_id(handler) # create it
      call_handlers[handler.Name] = handler # add it to the dictionary of all handlers
  
  print("setting business hours key mappings...")
  print("setting transfer rules...")
  print("uploading greetings...")
  print("setting access numbers (pilot identifiers)...\n")
  for handler in call_handlers.values():
    try:
      handler: CallHandler

      # set businss hours key mappings and transfer rules
      if handler.BusinessHoursKeyMapping and handler.BusinessHoursKeyMapping not in INVALID_OPTIONS and not pd.isna(handler.BusinessHoursKeyMapping):
        set_business_hours_keys_and_transfer_rules(handler, cn, call_handlers)

      # set business hours audio file greeting
      if handler.BusinessHoursMainMenuCustomPromptFilename and handler.BusinessHoursMainMenuCustomPromptFilename not in INVALID_OPTIONS and not pd.isna(handler.BusinessHoursMainMenuCustomPromptFilename):
        target_filename = handler.BusinessHoursMainMenuCustomPromptFilename.lower()
        audio_file_path = get_audio_file_path(target_filename, PATH_TO_AUDIO_FILES)
        
        if audio_file_path:
          cn.upload_greeting(audio_file_path, handler, 'Standard')
        else:
          _log_error(f"ERROR: audio file {audio_file_path} not found\n")

      elif handler.BusinessHoursWelcomeGreetingFilename and handler.BusinessHoursWelcomeGreetingFilename not in INVALID_OPTIONS and not pd.isna(handler.BusinessHoursWelcomeGreetingFilename):
        target_filename = handler.BusinessHoursWelcomeGreetingFilename.lower()
        audio_file_path = get_audio_file_path(target_filename, PATH_TO_AUDIO_FILES)
        
        if audio_file_path:
          cn.upload_greeting(audio_file_path, handler, 'Standard')
        else:
          _log_error(f"ERROR: audio file {audio_file_path} not found\n")

      # set access number
      if handler.PilotIdentifierList and handler.PilotIdentifierList not in INVALID_OPTIONS and not pd.isna(handler.PilotIdentifierList):
        cn.set_dtmf_access_id(handler)

      # configure settings for after hours
      # after hours cases:
      # - 1. main menu prompt is null. key is a dash that goes to another handler. interpret this as timeout -> go to handler. assume handler already exists. (157-umaa-02-main_spanish) (283-umaa-02-main_spanish)
      # - 2. main menu prompt has a filename. no key mappings. play a closed greeting. (283-UMAA-02-Main_Spanish)
      # - 3. main menu prompt has a filename. yes key mappings. create a new handler if it doesnt already exist with this filename. set greeting. set mappings. (311-UMAA-01-Main_Spanish has lewisnightmainspanish.wav)
      # - 4. both greeting and main menu have filenames. means it is playing two wav files back to back. but this is not possible in unity. so I will ignore this for now. (316-umaa-05-admin_spanish) (367-UMAA-03-Nurse-English)
      
      # case 1
      if (not handler.AfterHoursMainMenuCustomPromptFilename or handler.AfterHoursMainMenuCustomPromptFilename in INVALID_OPTIONS and handler.AfterHoursKeyMapping) and handler.AfterHoursKeyMapping and handler.AfterHoursKeyMapping not in INVALID_OPTIONS:
        set_after_hours_to_handler(handler, call_handlers, cn)

      # case 2
      elif handler.AfterHoursMainMenuCustomPromptFilename and handler.AfterHoursMainMenuCustomPromptFilename not in INVALID_OPTIONS and handler.AfterHoursWelcomeGreetingFilename and handler.AfterHoursWelcomeGreetingFilename in INVALID_OPTIONS and (not handler.AfterHoursKeyMapping or handler.AfterHoursKeyMapping in INVALID_OPTIONS):
        set_closed_greeting(handler, cn, audio_path_name=handler.AfterHoursMainMenuCustomPromptFilename)
      elif handler.AfterHoursMainMenuCustomPromptFilename and handler.AfterHoursMainMenuCustomPromptFilename in INVALID_OPTIONS and handler.AfterHoursWelcomeGreetingFilename and handler.AfterHoursWelcomeGreetingFilename not in INVALID_OPTIONS and (not handler.AfterHoursKeyMapping or handler.AfterHoursKeyMapping in INVALID_OPTIONS):
        set_closed_greeting(handler, cn, audio_path_name=handler.AfterHoursWelcomeGreetingFilename)

      # case 3
      elif handler.AfterHoursMainMenuCustomPromptFilename and handler.AfterHoursMainMenuCustomPromptFilename not in INVALID_OPTIONS and handler.AfterHoursKeyMapping and handler.AfterHoursKeyMapping not in INVALID_OPTIONS:
        create_new_after_hours_handler(handler, cn, call_handlers)

      # case 4
      elif handler.AfterHoursWelcomeGreetingFilename and handler.AfterHoursWelcomeGreetingFilename not in INVALID_OPTIONS and handler.AfterHoursMainMenuCustomPromptFilename and handler.AfterHoursMainMenuCustomPromptFilename not in INVALID_OPTIONS:
        pass

    except Exception as e:
      _log_error(f"Unexpected error while processing handler '{handler.Name}': {e}")
      continue


  

# TODO other conf might need to be done manually
# TODO: set schedules
# is there anything to set for settings during the greeting. allow them to record message after prompt??
# times to reprompt caller?
# after greeting take message?




"""
main program execution.
"""
if __name__ == "__main__":
  init_logs()
  print("starting program...")
  try:
    test()
  except Exception as e:
    _log_error(f"Fatal error in top-level execution: {e}")
  print("done.")