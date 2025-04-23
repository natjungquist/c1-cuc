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


"""
finds the specific business hours wav file 
from the directory with all the wav files.
"""
def get_audio_file_path(target_filename, path_to_audio_files):
  for filename in os.listdir(path_to_audio_files):
    if filename.endswith(".wav") and filename == target_filename:
        file_path = os.path.join(path_to_audio_files, filename)
        return file_path
    
"""
helper method get full 9 digit number because 
some handlers only specify a 4 digit extension.
"""
def get_full_number(extension, handler:CallHandler):
  return '80' + handler.prefix + extension

"""
sets all mappings for one call handler.
"""
def set_business_hours_keys_and_transfer_rules(handler:CallHandler, cn:CUCConnector, call_handlers):

  mapping_list = handler.BusinessHoursKeyMapping.split(';')
  for mapping in mapping_list:
    mapping_parts = mapping.split(',')

    transfer_to = None
    key = mapping_parts[0].strip()

    # TODO: sometimes key is - but it's not for operator
    # if key == '-':

    if (mapping_parts[2] != ''): # go to a number
      transfer_to = mapping_parts[2]

      if len(transfer_to) == 4: #only an extension was specified
        transfer_to = get_full_number(transfer_to, handler)

      if len(transfer_to) == 9: #must be 9 digits long to proceed
        if key == '-': #dash from customer data represents the operator
          key = '0'
          handler.set_transfer_rule_extension(transfer_to)
          cn.set_transfer_rule(handler)

        cn.set_dtmf_mapping(key, transfer_to, handler, is_to_number=True)
      else:
        print(f"ERROR: failed to parse business hours key mapping for handler {handler.Name}\n")

    elif (mapping_parts[3] != ''): # go to a another handler
      transfer_to = mapping_parts[3]

      handler_next = call_handlers.get(transfer_to)
      if handler_next:
        transfer_to = handler_next.get_id()

      if not transfer_to:
        print(f"ERROR: error getting id of handler to transfer to\n")
      else:
        cn.set_dtmf_mapping(key, transfer_to, handler, is_to_number=False)

    # try:
    #   if (mapping_parts[4] != ''): # go to a wav file
    #     transfer_to = mapping_parts[4]
    #     with open("dtmf_could_not_be_set_to_wav.txt", "a") as file:
    #       file.write(f"{handler.Name} -  key: {key}, {transfer_to}\n")

        # check if wav file exists
        # audio_file_path = get_audio_file_path(transfer_to, PATH_TO_AUDIO_FILES)
        # if not audio_file_path:
        #     with open("missing_wavs_for_businesshours_dtmf.txt", "a") as file:
        #       file.write(f"{transfer_to}\n")
        
    # except IndexError:
    #    print(f"index error on {handler.Name}: {handler.BusinessHoursKeyMapping} -- {mapping_parts}")

"""
assumes the handler always has only one after hours mapping
"""
def set_after_hours_rule(handler:CallHandler, cn:CUCConnector, call_handlers):
  mapping_list = handler.AfterHoursKeyMapping.split(';')

  for mapping in mapping_list:
    mapping_parts = mapping.split(',')

    transfer_to = None
    key = mapping_parts[0].strip()

    if (mapping_parts[2] != ''): # go to a number
      transfer_to = mapping_parts[2]

      if len(transfer_to) == 4: #only an extension was specified
        transfer_to = get_full_number(transfer_to, handler)

      if len(transfer_to) == 9: #must be 9 digits long to proceed
        pass # TODO
      else:
        print(f"ERROR: failed to parse after hours key mapping for handler {handler.Name}\n")

    elif (mapping_parts[3] != ''): # go to a another handler
      transfer_to = mapping_parts[3]

      handler_next = call_handlers.get(transfer_to)
      if handler_next:
        transfer_to = handler_next.get_id()

      if not transfer_to:
        print(f"ERROR: error getting id of handler to transfer to\n")
      else:
        pass # TODO




"""
main program execution.
"""
if __name__ == "__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  # source_audio_dir = os.path.join(os.getcwd(), "audioFiles")
  # convert_all_wav_files(source_audio_dir)

  # load in config items
  print("loading in config...\n")
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = config["autoAttendantsFile"]
  PATH_TO_AUDIO_FILES = os.path.join(os.getcwd(), "converted_wav_files") 
  INVALID_OPTIONS = ["0", 0, "silence.wav", "silence2.wav"]

  SERVER = config["server"]
  USERNAME = config["username"]
  PASSWORD = config["password"]
  cn = CUCConnector(SERVER, USERNAME, PASSWORD)
  cn.get_template_id()

  # set info for all handlers
  call_handlers = {} #key: name, value:handler

  df = pd.read_csv(FILE)

  # for getting handlers that reference .wav files in their dtmf mappings
  # for index, row in df.iterrows():
  #   handler = CallHandler(row)
  #   if handler.BusinessHoursKeyMappingEnabled:
  #     set_business_hours_keys_and_transfer_rules(handler, cn)

  print("creating handlers...")
  for index, row in df.iterrows():
      handler = CallHandler(row)
      cn.create_handler_and_get_id(handler)
      call_handlers[handler.Name] = handler
  
  print("\nsetting business hours key mappings...")
  print("setting transfer rules...")
  print("uploading greetings...")
  print("setting access numbers...")
  for handler in call_handlers.values():
    # set businss hours key mappings and transfer rules
    if handler.BusinessHoursKeyMappingEnabled:
      set_business_hours_keys_and_transfer_rules(handler, cn, call_handlers)

    # set business hours audio file greeting
    num_missing_wavs = 0

    if handler.BusinessHoursMainMenuCustomPromptFilename and handler.BusinessHoursMainMenuCustomPromptFilename not in INVALID_OPTIONS:
      target_filename = handler.BusinessHoursMainMenuCustomPromptFilename.lower()
      audio_file_path = get_audio_file_path(target_filename, PATH_TO_AUDIO_FILES)
      
      if audio_file_path:
        cn.upload_greeting(audio_file_path, handler)
      else:
        num_missing_wavs += 1
        print(f"ERROR: audio file {audio_file_path} not found\n")

    elif handler.BusinessHoursWelcomeGreetingFilename and handler.BusinessHoursWelcomeGreetingFilename not in INVALID_OPTIONS:
      target_filename = handler.BusinessHoursWelcomeGreetingFilename.lower()
      audio_file_path = get_audio_file_path(target_filename, PATH_TO_AUDIO_FILES)
      
      if audio_file_path:
        cn.upload_greeting(audio_file_path, handler)
      else:
        num_missing_wavs += 1
        print(f"ERROR: audio file {audio_file_path} not found\n")

    # set access extension
    if handler.PilotIdentifierList and handler.PilotIdentifierList not in INVALID_OPTIONS:
      cn.set_dtmf_access_id(handler)

    # TODO: after hours
    # if handler.AfterHoursWelcomeGreetingFilename and handler.AfterHoursWelcomeGreetingFilename not in INVALID_OPTIONS:
    #   pass
    # if handler.AfterHoursKeyMappingEnabled:
    #   make it transfer to the number ot handler specified
    # TODO: the AfterHoursMainMenuCustomPromptFilename do not correspond to after hours handler names
    # TODO: the AfterHoursKeyMappings do correspond to handler names

  if num_missing_wavs > 0:
    print(f"ERRORS: {num_missing_wavs} audio files not found for setting business hours menu prompt.\n")
  

  # TODO: set schedules


  # TODO sometimes there is an operatorextension but the - operator in the key mapping is different
  # TODO sometimes keymapping is false but there is a key mapping