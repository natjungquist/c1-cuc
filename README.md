# C1 CUC Automation 

## About

A specific customer of C1 has requested a way to automate a way to bulk export call handlers in Cisco Unified Communications (CUC). This program is designed to streamline the provisioning of call handlers in CUC for the client, making the migration process faster and more efficient. Given files detailing call handler configuration information, the program creates the call handlers, configures their DTMF mappings, sets their schedules, and uploads their existing greetings. The program is specifically tailored to process the format of data given by the client. 

## Prerequisites

* Data for call handlers to be migrated. Must be CSV format.
* Audio files/recordings saved together in a folder. Put this folder inside the `src` directory. 
* Cisco Unity Connection server credentials.
* Recommended application to run this program: VSCode.

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Python, pandas, and requests** (if not already installed)
   - Install python at [python.org](https://www.python.org/downloads/)
        - This program was developed with python 3.11.4
   - Install dependencies:
     ```bash
     pip install pandas
     pip install requests
     ```
   To run convert_wav_files.py, also install ffmpeg:
   - Download 7zip from: [7-zip.org](https://www.7-zip.org/download.html)
   - Download ffmpeg from: [ffmpeg.org](https://www.ffmpeg.org/download.html)
   - Extract ffmpeg with 7zip.
   - Add ffmpeg executable to your PATH.
   - Install python wrapper:
      ```bash
      pip install python-ffmpeg
      ```
3. **Make sure recordings are in the correct file format.**
- Cisco Unity Connection only accepts recordings of type RIFF (little-endian) data, WAVE audio, 16 bit, mono 8000 Hz. Run `convert_wav_files.py` 
4. **Create configuration file.**
- In `src` directory, create `config.json`:
   ```json
   {
      "server":"",
      "username":"",
      "password":"",
      "autoAttendantsFile":"",
      "recordingsDirectory":""
   }
   ```
## Run the Program
- `main.py`
## After Running the Program
- errors will be logged to `error.log`


## Contact 
- Developer: Natalie Jungquist, njungquist@onec1.com
- Manager: Tony Shroeder, tshroeder@onec1.com