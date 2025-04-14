# TODO (WIP)
# main

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
def get_business_hours_audio_file_path(handler:CallHandler):
  path_to_audio_files = os.getcwd() + '\\audioFiles'
  target_filename = handler.BusinessHoursMainMenuCustomPromptFilename.lower()
  
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
def set_business_hours_keys(handler:CallHandler):
  mapping_list = handler.BusinessHoursKeyMapping.split(';')
  for mapping in mapping_list:
    mapping_parts = mapping.split(',')

    key = mapping_parts[0].strip()
    transfer_to = mapping_parts[2]
    if len(transfer_to) > 9: #it is going to another call handler
      pass
    # TODO 
    else:
      if len(transfer_to) == 4: #only an extension was specified
        transfer_to = get_full_number(transfer_to, handler)

      if len(transfer_to) == 9:
        print(f"key: {key} num: {transfer_to}")
        cn.set_dtmf_mapping(key, transfer_to, handler)
      else:
        print(f"error: failed to parse businses hours key mapping for handler {handler.Name}")

"""
main program execution.
"""
if __name__ == "__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


  # load in config items
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = config["autoAttendantsFile"]
  SERVER = config["server"]
  USERNAME = config["username"]
  PASSWORD = config["password"]

  cn = CUCConnector(SERVER, USERNAME, PASSWORD)
  cn.get_template_id()

  df = pd.read_csv(FILE)

  data = df.iloc[0]
  test_handler = CallHandler(data)
  # print(data)
  # call_handlers = {}
  # for ... in file:
  #   get info, save to attendant object, save attendant dict

  # create the handlers
  cn.create_handler_and_get_id(test_handler)

  # set businss hours key mappings
  # set_business_hours_keys(test_handler)

  # TODO:
  # set transfer rule
  # TODO: why??

  # set business hours audio file greeting
  audio_file_path = get_business_hours_audio_file_path(test_handler)
  print(audio_file_path)
  # cn.upload_greeting(audio_file_path, test_handler)

  # set after hours audio file greeting
  # if AfterHoursWelcomeGreetingFilename is not silence.wav, create another handler and set its audio?



