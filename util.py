import ffmpeg
import platform
import re
import os
import pandas as pd

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