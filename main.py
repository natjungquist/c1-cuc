# main

# python -m pip install pandas
# python -m pip install ffmpeg-python
  # download ffmpeg exe. 7zip to Program Files\ffmpeg add to system path. 
from CUCConnector import CUCConnector
from CallHandler import CallHandler
import pandas as pd
import json
import os
import urllib3


INVALID_OPTIONS = ["0", 0, "", "silence.wav", "silence2.wav", '']

"""
finds the specific business hours wav file 
from the directory with all the wav files.
"""
def get_audio_file_path(target_filename, path_to_audio_files):
  for filename in os.listdir(path_to_audio_files):
    if filename.endswith(".wav") and filename == target_filename:
      file_path = os.path.join(path_to_audio_files, filename)
      return file_path
    elif filename.endswith(".wma") and filename[:-4] == target_filename:
      file_path = os.path.join(path_to_audio_files, filename)
      return file_path
    
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
  if handler.OperatorExtension not in INVALID_OPTIONS:
    cn.set_dtmf_mapping("0", handler.OperatorExtension, handler, is_to_number=True)

  # other mappings
  mapping_list = handler.BusinessHoursKeyMapping.split(';')
  has_dash = False
  for mapping in mapping_list:
    mapping_parts = mapping.split(',')
    if len(mapping_parts) < 4:
      print("ERROR: mapping parts")
      return # TODO

    transfer_to = None
    key = mapping_parts[0].strip()

    # option 1. go to a number
    if (mapping_parts[2] != ''):
      transfer_to = mapping_parts[2]
      if len(transfer_to) == 4: #only an extension was specified
        transfer_to = get_full_number(transfer_to, handler)

      #must be 9 digits long to proceed
      if len(transfer_to) == 9: 
        if key == '-': #dash from customer data represents timeout
          has_dash = True
          handler.set_transfer_rule_extension(transfer_to)
          cn.set_transfer_rule(handler)
        else: #not a dash, set mapping
          cn.set_dtmf_mapping(key, transfer_to, handler, is_to_number=True)
      else:
        print(f"ERROR: could not make 9-digit key mapping for handler {handler.Name}\n")

    # option 2. go to another call handler that already exists
    elif (mapping_parts[3] != ''): #TODO not in 
      transfer_to = mapping_parts[3]

      handler_next = call_handlers.get(transfer_to)
      if handler_next:
        transfer_to = handler_next.get_id()
      else:
        transfer_to = None

      if not transfer_to:
        print(f"ERROR: error getting id of handler to transfer to\n")
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
        cn.upload_greeting(audio_file_path, new_handler)
      else:
        print(f"ERROR: audio file {audio_file_path} not found\n")   

      # set this call handler to map to the new handler
      cn.set_dtmf_mapping(key, new_handler.get_id(), handler, is_to_number=False)
    
    # set the transfer rule to the OperatorExtension if there was not already one specified
    if not has_dash:
      if handler.OperatorExtension not in INVALID_OPTIONS:
        handler.set_transfer_rule_extension(handler.OperatorExtension)
        cn.set_transfer_rule(handler)


"""
main program execution.
"""
if __name__ == "__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  # load in config items
  print("loading in config...\n")
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = config["autoAttendantsFile"]
  PATH_TO_AUDIO_FILES = os.path.join(os.getcwd(), "converted_wav_files") 

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
    handler: CallHandler

    # set businss hours key mappings and transfer rules
    if handler.BusinessHoursKeyMapping not in INVALID_OPTIONS:
      set_business_hours_keys_and_transfer_rules(handler, cn, call_handlers)

    # set business hours audio file greeting # TODO
    if handler.BusinessHoursMainMenuCustomPromptFilename not in INVALID_OPTIONS:
      target_filename = handler.BusinessHoursMainMenuCustomPromptFilename.lower()
      audio_file_path = get_audio_file_path(target_filename, PATH_TO_AUDIO_FILES)
      
      if audio_file_path:
        cn.upload_greeting(audio_file_path, handler)
      else:
        print(f"ERROR: audio file {audio_file_path} not found\n")

    elif handler.BusinessHoursWelcomeGreetingFilename not in INVALID_OPTIONS:
      target_filename = handler.BusinessHoursWelcomeGreetingFilename.lower()
      audio_file_path = get_audio_file_path(target_filename, PATH_TO_AUDIO_FILES)
      
      if audio_file_path:
        cn.upload_greeting(audio_file_path, handler)
      else:
        print(f"ERROR: audio file {audio_file_path} not found\n")

    # set access extension
    if handler.PilotIdentifierList not in INVALID_OPTIONS:
      cn.set_dtmf_access_id(handler)

    # TODO: after hours
    # after hours cases:
    # - main menu prompt is null. key mapping goes to another handler, assume it already exists. (157-umaa-02-main_spanish)
    # - main menu prompt has a filename. no key mappings. play a closed greeting. (283-umaa-02-main_spanish)
    # - main menu prompt has a filename. yes key mappings. create a new handler if it doesnt already exist with this filename. set greeting. set mappings. (311-UMAA-01-Main_Spanish has lewisnightmainspanish.wav)
    # - both greeting and main menu have filenames. means it is playing two wav files back to back. but this is not possible in unity. so I will ignore this for now. (316-umaa-05-admin_spanish) 
  

  # TODO: set schedules

# TODO other conf
# is there anything to set for settings during the greeting. allow them to record message after prompt??
# times to reprompt caller?
# after greeting take message?

