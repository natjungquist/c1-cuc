import ffmpeg
import os
import urllib3

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
main program execution.
"""
if __name__ == "__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  source_audio_dir = os.path.join(os.getcwd(), "audioFiles")
  convert_all_wav_files(source_audio_dir)