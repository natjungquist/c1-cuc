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
logs success messages to a file
"""
def _log_success(info: str):
  _log_to_file('successes.txt', info)

"""
logs error messages to a file
"""
def _log_error(info: str):
  _log_to_file('errors.txt', info)