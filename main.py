# TODO (WIP)
# main

from CUCConnector import CUCConnector
from CallHandler import CallHandler
import pandas as pd
import json

if __name__ == "__main__":

  # load in config items
  with open('config.json') as config_file:
    config = json.load(config_file)

  FILE = config["autoAttendantsFile"]

  SERVER = config["server"] # dev mode: "https://10.0.0.64"
  USERNAME = config["username"]
  PASSWORD = config["password"]

  # df = pd.read_csv(FILE)

  # first = df.iloc[1]
  # print(first_handler)

  cn = CUCConnector(SERVER, USERNAME, PASSWORD)
  cn.get_template_id()

  test = CallHandler("test_python")
  cn.create_handler_and_get_id(test)
  print("new handler id: "+test.get_id())

  # TESTING
  # testpath = "./tmp.zip"
  # handler_id = "ef98b1b5-4b17-4685-a459-c863ba9640da"
  # extract_dir = "temp_wav_files"
  # test_attendant = AutoAttendant(handler_id)
  # cn.upload_greeting(testpath, extract_dir, test_attendant)

  call_handlers = {}
  # for ... in file:
  #   get info, save to attendant object, save attendant dict


