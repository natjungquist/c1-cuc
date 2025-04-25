# Utility program to compare all WAV files specified in the handler data to the WAV files
# that this project contains. If any cannot be found, the names of the missing WAV files 
# are printed out to a log file.

# python -m pip install pandas
from CallHandler import CallHandler
import pandas as pd
import json
import os
import sys

INVALID_OPTIONS = ["0", 0, "silence.wav", "silence2.wav", '']

"""
finds the specific business hours wav file 
from the directory with all the wav files.

args:
  target_filename: name of file we are looking for
  path_to_audio_files: absolute path to the directory containing all audio files

returns:
  the absolute path to the audio file we are looking for.
  None if it does not exist.
"""
def get_audio_file_path(target_filename, path_to_audio_files):
  target_filename = target_filename.lower()

  for filename in os.listdir(path_to_audio_files):
    filename = filename.lower()

    if filename.endswith(".wav"):
      if filename == target_filename or filename.startswith(target_filename) or target_filename.startswith(filename):
        file_path = os.path.join(path_to_audio_files, filename)
        return file_path
      
    elif filename.endswith(".wma"):
      if filename[:-4] == target_filename or filename.startswith(target_filename[:-4]) or target_filename.startswith(filename):
        file_path = os.path.join(path_to_audio_files, filename)
        return file_path[:-4]
      
    if filename.startswith('023-umaa-01-english_main') and target_filename.startswith('023-umaa-01-english_main'):
       pass
    # we want english main but we have main english

  return None
    
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
Asks the user for the filename they want to log the missing wav files to.
"""
def get_log_file_name():
  while True:
    user_input = input("Please enter the name of the log file for missing WAVs (or press Enter to use 'missing_wavs.txt' in the current directory): ").strip()
    if not user_input:
      default_name = "missing_wavs.txt"
      print(f"Using default file name: {default_name}")
      return default_name
    else:
       return user_input

"""
main program execution.
"""
if __name__ == "__main__":

  # load in config items
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = config["autoAttendantsFile"]
  PATH_TO_AUDIO_FILES = os.path.join(os.getcwd(), "UMWAVFiles") 

  MISSING_WAVS_LOGFILE = get_log_file_name()
  with open(MISSING_WAVS_LOGFILE, "w") as log_file:
    log_file.write("MISSING AUDIO FILE NAMES\n")
     
  # set info for all handlers
  call_handlers = {} #key: name, value:handler
  df = pd.read_csv(FILE)

  # check all the handlers' info
  for index, row in df.iterrows():
      handler = CallHandler(row)
      call_handlers[handler.Name] = handler

      if handler.BusinessHoursKeyMapping and handler.BusinessHoursKeyMapping not in INVALID_OPTIONS and not pd.isna(handler.BusinessHoursKeyMapping):
         mapping_list = handler.BusinessHoursKeyMapping.split(';')
         for mapping in mapping_list:
            mapping_parts = mapping.split(',')
            if len(mapping_parts) < 4:
              print("ERROR: business hours mapping parts")
              print(handler.Name)
              sys.exit()
            if (mapping_parts[4] not in INVALID_OPTIONS): # this mapping goes to a wav file
              filename = mapping_parts[4]
              audio_file_path = get_audio_file_path(filename, PATH_TO_AUDIO_FILES)
              print(audio_file_path)
              if not audio_file_path:
                 _log_to_file(MISSING_WAVS_LOGFILE, filename)

      if handler.AfterHoursKeyMapping and handler.AfterHoursKeyMapping not in INVALID_OPTIONS and not pd.isna(handler.AfterHoursKeyMapping):
         mapping_list = str(handler.AfterHoursKeyMapping).split(';')
         for mapping in mapping_list:
            mapping_parts = mapping.split(',')
            if len(mapping_parts) < 4:
              print("ERROR: after hours mapping parts")
              print(handler.Name)
              sys.exit()
            if (mapping_parts[4] not in INVALID_OPTIONS): # this mapping goes to a wav file
              filename = mapping_parts[4]
              audio_file_path = get_audio_file_path(filename, PATH_TO_AUDIO_FILES)
              if not audio_file_path:
                 _log_to_file(MISSING_WAVS_LOGFILE, filename)

      if handler.BusinessHoursWelcomeGreetingFilename and handler.BusinessHoursWelcomeGreetingFilename not in INVALID_OPTIONS and not pd.isna(handler.BusinessHoursWelcomeGreetingFilename):
          filename = handler.BusinessHoursWelcomeGreetingFilename
          audio_file_path = get_audio_file_path(filename, PATH_TO_AUDIO_FILES)
          if not audio_file_path:
            _log_to_file(MISSING_WAVS_LOGFILE, filename)

      if handler.BusinessHoursMainMenuCustomPromptFilename and handler.BusinessHoursMainMenuCustomPromptFilename not in INVALID_OPTIONS and not pd.isna(handler.BusinessHoursMainMenuCustomPromptFilename):
          filename = handler.BusinessHoursMainMenuCustomPromptFilename
          audio_file_path = get_audio_file_path(filename, PATH_TO_AUDIO_FILES)
          if not audio_file_path:
            _log_to_file(MISSING_WAVS_LOGFILE, filename)

      if handler.AfterHoursWelcomeGreetingFilename and handler.AfterHoursWelcomeGreetingFilename not in INVALID_OPTIONS and not pd.isna(handler.AfterHoursWelcomeGreetingFilename):
          filename = handler.AfterHoursWelcomeGreetingFilename
          audio_file_path = get_audio_file_path(filename, PATH_TO_AUDIO_FILES)
          if not audio_file_path:
            _log_to_file(MISSING_WAVS_LOGFILE, filename)
            
      if handler.AfterHoursMainMenuCustomPromptFilename and handler.AfterHoursMainMenuCustomPromptFilename not in INVALID_OPTIONS and not pd.isna(handler.AfterHoursMainMenuCustomPromptFilename):
          filename = handler.AfterHoursMainMenuCustomPromptFilename
          audio_file_path = get_audio_file_path(filename, PATH_TO_AUDIO_FILES)
          if not audio_file_path:
            _log_to_file(MISSING_WAVS_LOGFILE, filename)

  print("done")

      

  