# C1 CUC Automation 

## About

A specific customer of C1 has requested a way to automate a way to bulk export call handlers in Cisco Unified Communications (CUC). This program is designed to streamline the provisioning of call handlers in CUC for the client, making the migration process faster and more efficient. Given files detailing call handler configuration information, the program creates the call handlers, configures their DTMF mappings, sets their schedules, and uploads their existing greetings. The program is specifically tailored to process the format of data given by the client. 

## Prerequisites

* be a valid C1 engineer

## Installation - DEVELOPMENT MODE

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

3. **Install Python and pandas** (if not already installed)
   - Install python at [python.org](https://www.python.org/downloads/)
        - This program was developed with python 3.11.4
   - Install dependencies:
     ```bash
     pip install pandas
     ```


## Contact 
- Developer: Natalie Jungquist, njungquist@onec1.com
- Manager: Tony Shroeder, tshroeder@onec1.com