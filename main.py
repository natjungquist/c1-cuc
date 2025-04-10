# TODO (WIP)
# main

from CUCConnector import CUCConnector
from CallHandler import CallHandler
import pandas as pd
import json
import os

"""
finds the specific business hours wav file 
from the directory with all the wav files.
"""
def get_business_hours_audio_file_path(handler:CallHandler):
  path_to_audio_files = '/audioFiles'
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
  prefix = handler.get_name()[0:4]
  return '80' + prefix + extension

"""
sets all mappings for one call handler.
"""
def set_all_dtmf_mappings(handler:CallHandler):
  BusinessHoursKeyMapping = "1,Attendance and Enrollment,7000,,,,,,,; 2,Nurse,3050,,,,,,,; 9,Cesia,3022,,,,,,,; -,Operator,3021,,,,,,,"
  # mapping_list = handler.BusinessHoursKeyMapping.split(';')
  mapping_list = BusinessHoursKeyMapping.split(';')
  for mapping in mapping_list:
    mapping_parts = mapping.split(',')

    key = mapping_parts[0]
    transfer_number = mapping_parts[2]
    if len(transfer_number) == 4:
      transfer_number = get_full_number(transfer_number, handler)

    cn.set_dtmf_mapping(key, transfer_number, handler)

"""
main program execution.
"""
if __name__ == "__main__":

  # load in config items
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = config["autoAttendantsFile"]
  SERVER = config["server"]
  USERNAME = config["username"]
  PASSWORD = config["password"]

  cn = CUCConnector(SERVER, USERNAME, PASSWORD)
  cn.get_template_id()

  # df = pd.read_csv(FILE)

  # first = df.iloc[1]
  # print(first_handler)

  handler = CallHandler("test_python")
  cn.create_handler_and_get_id(handler)

  set_all_dtmf_mappings(handler)

  # audio_file_path = get_business_hours_audio_file_path(handler)
  # cn.upload_greeting(audio_file_path, handler)
  # if AfterHoursWelcomeGreetingFilename is not silence.wav, create another handler and set its audio?

  call_handlers = {}
  # for ... in file:
  #   get info, save to attendant object, save attendant dict


