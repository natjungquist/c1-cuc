# TODO (WIP)
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
import ffmpeg
import platform

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
        if key == '-':
          key = '0'
          handler.set_transfer_rule_extension(transfer_to)
        print(f"key: {key} num: {transfer_to}")
        cn.set_dtmf_mapping(key, transfer_to, handler)
      else:
        print(f"error: failed to parse businses hours key mapping for handler {handler.Name}")

"""
converts the Microsoft ASF file to RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 8000 Hz
"""
def convert_to_wav(audio_file_path):
  # print(platform.system())
  output_path = os.getcwd() + f'\\audioFiles\\{audio_file_path}'
  try:
    (
      ffmpeg
      .input(audio_file_path)
      .output(output_path, ar=8000, ac=1, sample_fmt='s16', format='wav', acodec='pcm_s16le')
      .run(overwrite_output=True)
    )
  except ffmpeg.Error as e:
    print("ffmpeg: " + e.stderr.decode())

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

  # set transfer rule
  # cn.set_transfer_rule(test_handler.transfer_rule_extension, test_handler)

  # set business hours audio file greeting
  # audio_file_path = get_business_hours_audio_file_path(test_handler)
  # convert_to_wav(audio_file_path)
  # cn.upload_greeting(audio_file_path, test_handler)

  # TODO: test dtmf going to another handler
  # TODO: confirm that - is only time to set transfer rule
  # TODO: account for NULLS
  # TODO: figure out which to create first
  # TODO: after hours
  # TODO: set schedules

  


  # set after hours audio file greeting
  # if AfterHoursWelcomeGreetingFilename is not silence.wav, create another handler and set its audio?



