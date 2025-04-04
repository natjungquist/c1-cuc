# TODO (WIP)
# main

from CUCConnector import CUCConnector
from AutoAttendant import AutoAttendant
import pandas as pd
import json

if __name__ == "__main__":

  # load in config items
  with open('config.json') as config_file:
    config = json.load(config_file)

  CALLER_INPUT_FILE = config["callerInput"]["file"]
  CALLER_INPUT_COLS = config["callerInput"]["columns"]

  SCHEDULES_CONFIG_FILE = config["schedules"]["file"]
  SCHEDULES_COLS = config["schedules"]["columns"]

  META_FILE = config["autoAttendants"]["file"]
  META_COLS = config["autoAttendants"]["columns"]

  SERVER = config["server"] # dev mode: "https://10.0.0.64"
  USERNAME = config["username"]
  PASSWORD = config["password"]

  caller_input_data = pd.read_csv(CALLER_INPUT_FILE, usecols=CALLER_INPUT_COLS)

  cn = CUCConnector(SERVER, USERNAME, PASSWORD)

  # TESTING
  testpath = "./tmp.zip"
  handler_id = "ef98b1b5-4b17-4685-a459-c863ba9640da"
  extract_dir = "temp_wav_files"
  test_attendant = AutoAttendant(handler_id)
  cn.upload_greeting(testpath, extract_dir, test_attendant)

  call_handlers = {}
  # for ... in file:
  #   get info, save to attendant object, save attendant dict


