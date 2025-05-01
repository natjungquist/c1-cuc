# Utility program to convert all audio files in a specified directory to the specific 
# format of .wav file that the CUC API expects to recieve.
# Run this program from the c1-cuc/src directory.

import ffmpeg
import os

"""
converts the Microsoft ASF or WMA file to RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 8000 Hz
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
    print("ffmpeg error.")

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
      if os.path.isfile(input_path) and not input_path.endswith('.csv'):
          name, _ = os.path.splitext(filename)
          output_path = os.path.join(output_dir, name)
          convert_to_wav(input_path, output_path)

"""
Asks the user for the directory containing the WAV files.
Returns the absolute path to the directory.
"""
def get_source_audio_directory():
  while True:
    user_input = input("Please enter the directory containing the WAV files (or press Enter for 'UMWAVFiles' in the current directory): ").strip()
    if not user_input:
      default_path = os.path.join(os.getcwd(), "UMWAVFiles")
      print(f"Using default directory: {default_path}")
      return default_path
    elif os.path.isdir(user_input):
      return os.path.abspath(user_input)
    else:
      print("Invalid directory path. Please try again.")

"""
main program execution.
"""
if __name__ == "__main__":
  source_audio_dir = get_source_audio_directory()
  convert_all_wav_files(source_audio_dir)
  print("WAV file conversion complete.")
  print("File type: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 8000 Hz.")