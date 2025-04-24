# main

# python -m pip install pandas
from CallHandler import CallHandler
import pandas as pd
import json
import os

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
writes a missing audio filename to a log file.

args:
    filename: The name of the log file to write to.
    transfer_target: The identifier (e.g., transfer_to) associated with the missing file.
"""
def _log_to_file(filename: str, info_to_write: str):
    try:
        with open(filename, "a") as log_file:
            log_file.write(f"{info_to_write}\n")
    except Exception as e:
        print(f"ERROR: could not write to log file '{filename}': {e}\n")


"""
main program execution.
"""
if __name__ == "__main__":

  # load in config items
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = config["autoAttendantsFile"]
  PATH_TO_AUDIO_FILES = os.path.join(os.getcwd(), "converted_wav_files") 
  INVALID_OPTIONS = ["0", 0, "silence.wav", "silence2.wav"]

  MISSING_WAVS_LOGFILE = "missing_wavs.txt"

  # set info for all handlers
  call_handlers = {} #key: name, value:handler

  df = pd.read_csv(FILE)

  # check all the handlers' info
  for index, row in df.iterrows():
      handler = CallHandler(row)
      call_handlers[handler.Name] = handler

      # _log_to_file(MISSING_WAVS_FILE, transfer_to)
  

    # TODO: after hours
    # if handler.AfterHoursWelcomeGreetingFilename and handler.AfterHoursWelcomeGreetingFilename not in INVALID_OPTIONS:
    #   pass
    # if handler.AfterHoursKeyMappingEnabled:
    #   make it transfer to the number ot handler specified
    # TODO: the AfterHoursMainMenuCustomPromptFilename do not correspond to after hours handler names
    # TODO: the AfterHoursKeyMappings do correspond to handler names
  