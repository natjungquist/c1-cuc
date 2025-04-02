# TODO (WIP)
# main

from CUCConnector import CUCConnector
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

  SERVER = config["serverName"] # dev mode: "https://10.0.0.64"
  USERNAME = config["userName"]
  PASSWORD = config["password"]

  caller_input_data = pd.read_csv(CALLER_INPUT_FILE, usecols=CALLER_INPUT_COLS)

  cn = CUCConnector(SERVER, USERNAME, PASSWORD)

  # TESTING
  testpath = "./tmp.zip"
  handler_id = "ef98b1b5-4b17-4685-a459-c863ba9640da"
  extract_dir = "temp_wav_files"
  cn.upload_greeting(testpath, extract_dir, handler_id)


  # class AttendantProvisioner
  # save all the auto attendant names in a dict
  # identify the auto attendants that need to be made first

  # create them with CUCConnector
  # save their ids in the dict

  # with CUCConnector:
  # set their caller input values
  # set other data
  # TODO
  # ...
