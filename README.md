# ndai-denhub

## Desktop App - Dev. Plan (2025/03/08, Kyi) 
  - Use Mattermost Baseline Framework 
    - https://github.com/mattermost/desktop 
  - Flow of App (Billing Agent) Processing: 
    - User Inputs Insurance Pdfs of EOB 
    - Call DenHub OCR Server - Extract Bill Data 
    - Call OpenDental MySQL Server - Extract Claim Data 
    - (Run Billing Agent for each insurance pdf format)
  - ETC.   

## Demo Server - Setup @ Ubuntu 22.04 (2025/03/08, Kyi)
- python3.10 venv setup 
  - sudo apt install python3-venv
  - sudo apt install python3-pip
  - python3 -m venv ~/.venv/ndai
  - source ~/.venv/ndai/bin/activate
- python3.10 venv 환경에서,
  - pip install -r requirements.txt
- Start streamlit server (Web - Demo Client)
  - bash run-st-server.sh 
- Start fastapi server (OCR - API Server)
  - bash run-api-server.sh 
