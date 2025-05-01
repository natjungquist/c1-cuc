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

SUCCESS_LOG_NAME = "success.log"
ERROR_LOG_NAME = "error.log"

"""
logs success messages to a file.
"""
def _log_success(info: str):
  _log_to_file(SUCCESS_LOG_NAME, info)

"""
logs error messages to a file.
"""
def _log_error(info: str):
  _log_to_file(ERROR_LOG_NAME, info)

"""
initializes log files with titles.
"""
def init_logs():
  with open(SUCCESS_LOG_NAME, "w") as success_file:
    success_file.write("Successful function calls:\n")

  with open(ERROR_LOG_NAME, "w") as error_file:
    error_file.write("Program errors (must fix these handlers manually):\n")