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
import re
from collections import defaultdict, deque

PATH_TO_AUDIO_FILES = os.path.join(os.getcwd(), "audioFiles") # TODO converted_audio_files

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
def set_business_hours_keys_and_transfer_rules(handler:CallHandler, cn:CUCConnector): # TODO all_handers
  if handler.BusinessHoursKeyMapping == "0" or not handler.BusinessHoursKeyMapping:
    with open("handlers_with_0_dtmf.txt", "a") as file:
      file.write(f"{handler.Name}\n")
      return
      
  mapping_list = handler.BusinessHoursKeyMapping.split(';')
  for mapping in mapping_list:
    mapping_parts = mapping.split(',')

    transfer_to = None
    key = mapping_parts[0].strip()
    
    # if (mapping_parts[2] != ''): # go to a number
    #   transfer_to = mapping_parts[2]

    #   if len(transfer_to) == 4: #only an extension was specified
    #     transfer_to = get_full_number(transfer_to, handler)

    #   if len(transfer_to) == 9: #must be 9 digits long to proceed
    #     if key == '-': #dash from customer data represents the operator
    #       key = '0'
    #       handler.set_transfer_rule_extension(transfer_to)
    #       cn.set_transfer_rule(handler)

    #     print(f"key: {key} num: {transfer_to}")
    #     cn.set_dtmf_mapping(key, transfer_to, handler, is_to_number=True)
    #   else:
    #     print(f"error: failed to parse businses hours key mapping for handler {handler.Name}\n")

    # elif (mapping_parts[3] != ''): # go to a another handler
    #   transfer_to = mapping_parts[3]

    #   handler_next = all_handlers.get(transfer_to.get_name())
    #   if handler_next:
    #     transfer_to = handler_next.get_id()
    #     print(f"key: {key} handler id: {transfer_to}")

    #   if not transfer_to:
    #     print(f"error getting id of handler to transfer to\n")
    #   else:
    #     cn.set_dtmf_mapping(key, transfer_to, handler, is_to_number=False)

    try:
      if (mapping_parts[4] != ''): # go to a wav file
        transfer_to = mapping_parts[4]

        # check if wav file exists
        audio_file_path = get_audio_file_path(transfer_to, PATH_TO_AUDIO_FILES)
        if not audio_file_path:
            with open("missing_wav_files.txt", "a") as file:
              file.write(f"{transfer_to}\n")
        else:
            with open("found_wav_files.txt", "a") as file:
              file.write(f"{transfer_to}\n")
    except IndexError:
       with open("index_error.txt", "a") as file:
        file.write(handler.BusinessHoursKeyMapping)
        file.write(mapping)
        print(mapping_parts)
        file.write(f"{handler.Name}\n")
        file.write("\n")
        return
      


"""
converts the Microsoft ASF file to RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 8000 Hz
"""
def convert_to_wav(input_path, output_path):
  # print(platform.system())
  try:
    (
      ffmpeg
      .input(input_path)
      .output(output_path, ar=8000, ac=1, sample_fmt='s16', format='wav', acodec='pcm_s16le')
      .run(overwrite_output=True)
    )
  except ffmpeg.Error as e:
    print("ffmpeg: " + e.stderr.decode())

"""
converts all files to proper format
"""
def convert_all_wav_files(source_dir):
  program_dir = os.getcwd()
  output_dir = os.path.join(program_dir, "converted_wav_files")

  if not os.path.exists(output_dir):
      os.makedirs(output_dir)

  for filename in os.listdir(source_dir):
      input_path = os.path.join(source_dir, filename)
      if os.path.isfile(input_path):
          name, _ = os.path.splitext(filename)
          output_path = os.path.join(output_dir, name + ".wav")
          convert_to_wav(input_path, output_path)

"""
finds some handlers that have business hours key mappings that reference other handlers
"""
def extract_referenced_handlers(df: pd.DataFrame) -> pd.DataFrame:
    referenced_handlers = set()

    handler_pattern = re.compile(r"\d{3}-UMAA-[\w\-]+(?!\.wav(?:$|\s))")

    # Step 1: Check each row for referenced handler names
    for mapping in df["BusinessHoursKeyMapping"].dropna():
        matches = handler_pattern.findall(mapping)
        referenced_handlers.update(matches)

    # Normalize the referenced handlers (e.g., lowercase) to avoid case mismatch issues
    referenced_handlers = {name.lower() for name in referenced_handlers}

    # Step 2: Ensure the 'Name' column is also normalized to lowercase for comparison
    df["Name"] = df["Name"].str.strip().str.lower()

    # Step 3: Create a new DataFrame that only includes handlers that are referenced
    df_referenced = df[df["Name"].isin(referenced_handlers)]

    missing_handlers = referenced_handlers - set(df["Name"])

    # Step 5: Save the missing handlers to a separate file
    output_file = "test_2.txt"
    if missing_handlers:
        missing_handlers_df = pd.DataFrame(list(missing_handlers), columns=["wav file"])
        missing_handlers_df.to_csv(output_file, index=False)
        print(f"wav file references saved to {output_file}")

    # Optional: print or log the referenced handler names
    print(f"Number of referenced handlers or wav files: {len(referenced_handlers)}")
    print(f"Number of referenced handlers found in df: {len(df_referenced)}")
    print("Referenced handler names found in BusinessHoursKeyMapping:")
    for name in referenced_handlers:
        print(name)

    # Return the DataFrame with only referenced handlers
    return df_referenced


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

  SERVER = config["server"]
  USERNAME = config["username"]
  PASSWORD = config["password"]
  cn = CUCConnector(SERVER, USERNAME, PASSWORD)

  df = pd.read_csv(FILE)
  for index, row in df.iterrows():
      test_handler = CallHandler(row)
      set_business_hours_keys_and_transfer_rules(test_handler, cn)
      target_filename = test_handler.BusinessHoursMainMenuCustomPromptFilename.lower()
      audio_file_path = get_audio_file_path(target_filename, PATH_TO_AUDIO_FILES)
      if not audio_file_path:
        with open("missing_wav_files.txt", "a") as file:
          file.write(f"{target_filename}\n")
      else:
        with open("found_wav_files.txt", "a") as file:
          file.write(f"{target_filename}\n")

  # data = df.iloc[0]
  # test_handler = CallHandler(data)
  # print(data)


  
  # cn.get_template_id()

  # set info for all handlers
  # call_handlers = {}
  

  # create the handlers
  # cn.create_handler_and_get_id(test_handler)

  # set businss hours key mappings and transfer rules
  # set_business_hours_keys_and_transfer_rules(test_handler, cn)
  # TODO: test dtmf going to another handler
  # TODO: account for NULLS

  # # set business hours audio file greeting
  # target_filename = test_handler.BusinessHoursMainMenuCustomPromptFilename.lower()
  # audio_file_path = get_audio_file_path(target_filename, path_to_audio_files)
  # if not audio_file_path:
  #   with open("missing_wav_files.txt", "a") as file:
  #     file.write(f"{target_filename}\n")
  # else:
  #   with open("found_wav_files.txt", "a") as file:
  #     file.write(f"{target_filename}\n")
  
  # cn.upload_greeting(audio_file_path, test_handler)

  # TODO: after hours
  # TODO: set schedules

  # TODO: set pilot identifier
  # cn.set_dmf_access_id(test_handler)

  # TODO sometimes there is an operatorextension but the - operator in the key mapping is different

  


  # set after hours audio file greeting
  # if AfterHoursWelcomeGreetingFilename is not silence.wav, create another handler and set its audio?



