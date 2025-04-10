# TODO (WIP)
# main

from CUCConnector import CUCConnector
from CallHandler import CallHandler
import pandas as pd
import json
import os

"""
finds the specific business hours wav file from the directory with all the wav files
"""
def get_business_hours_audio_file_path(handler:CallHandler):
  path_to_audio_files = '/audioFiles'
  target_filename = handler.BusinessHoursMainMenuCustomPromptFilename.lower()
  
  for filename in os.listdir(path_to_audio_files):
    if filename.endswith(".wav") and filename == target_filename:
        file_path = os.path.join(path_to_audio_files, filename)
        return file_path

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

  test = CallHandler("test_python")
  cn.create_handler_and_get_id(test)


  # audio_file_path = get_business_hours_audio_file_path(handler)
  # cn.upload_greeting(audio_file_path, handler)

  call_handlers = {}
  # for ... in file:
  #   get info, save to attendant object, save attendant dict


