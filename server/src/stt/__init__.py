import librosa
import numpy as np
import requests
import base64
from io import BytesIO
import json
import streamlit as st

from websockets.sync.client import connect
from scipy.io.wavfile import write as audio_write

# 덴스퍼 1 서버
densper1_url = "http://175.209.148.123:32379/transcribe" # whisper v3
# densper1_url = "http://175.209.148.123:8000/transcribe" # whisper v2

# 덴스퍼 2 서버
lang_map = {
    "ko": "ws://175.209.148.123:20010",
    "en": "ws://3.99.32.33:20011",
    "cn": "ws://192.168.1.219:20012",
    "ml3": "ws://192.168.1.219:20101"
}

#tts_url = "http://192.168.1.220:20300/generate-audio"
tts_url = "http://175.209.148.123:20300/generate-audio"

# (STT - Resampling) --------------------------------------------------
def resampling(audio):
    audio_sr = audio["sampling_rate"]
    audio_y = audio["raw"]

    # audio_data - resample and map to int16
    audio_data = librosa.resample(audio_y, orig_sr=audio_sr, target_sr=target_sr)
    audio_data = audio_data * max_int16
    return audio_data.astype(np.int16)

# (STT - Densper1) ----------------------------------------------------
def run_asr_densper1(audio, input_lang):
    sr = None
    if audio is None:
        st.toast("No audio input. Please upload an audio file or record a voice message")
        return "Cannot detect audio input"
    if isinstance(audio, st.runtime.uploaded_file_manager.UploadedFile) or isinstance(audio, np.ndarray):
        raw, sr = librosa.load(audio, sr=None)
        audio = {"sampling_rate": sr, "raw": raw}
    
    audio_data = resampling(audio)
    wav_bytes = BytesIO()  # 메모리 버퍼 생성
    audio_write(wav_bytes, sr, audio_data)  # WAV 데이터 작성
    wav_bytes.seek(0)  # 버퍼의 시작 위치로 이동
    wav_bytes = wav_bytes.read()  # 버퍼의 내용을 읽음

    wav_base64 = base64.b64encode(wav_bytes).decode("utf-8")
    
    # -- Request REST --
    payload = {
            "pcmorfile": wav_base64,
            "type": "pcm",
            "language": None if input_lang == "ml3" else input_lang,
            "initialPrompt": "",
            "patient": "",
            "device_id": "device"
        }
    
    response = requests.request(
        method="POST", 
        url=densper1_url, 
        headers={
            "Content-Type": "application/json"
        },
        json=payload)
    result = json.loads(response.text)
    return result["text"]

# (STT - Densper2) ----------------------------------------------------
#spkr_id = "dcai_web_demo"
spkr_id = ""
spkr_ctxt = ""
target_sr = 16000
max_int16 = 2**15

def transcribe(audio, version="densper1"):
    '''
    Preprocessing raw mircrophone audio data
    '''
    sr, y = audio
    
    # Convert to mono if stereo
    if y.ndim > 1:
        y = y.mean(axis=1)
        
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))

    return run_asr({"sampling_rate": sr, "raw": y}, version)

def run_asr_densper2(audio, spkr_lang="ko"):
    srv_den2 = lang_map[spkr_lang]
    
    if audio is None:
        st.toast("No audio input. Please upload an audio file or record a voice message")
        return "Error in processing"
    if isinstance(audio, st.runtime.uploaded_file_manager.UploadedFile) or isinstance(audio, np.ndarray):
        raw, sr = librosa.load(audio, sr=None)
        audio = {"sampling_rate": sr, "raw": raw}
    
    audio_data = resampling(audio)
    # -- connect websocket --
    ws = connect(srv_den2)
        
    # (1) send start msg
    start_msg = {
        "signal": "start",
        "nbest": 1, 
        "continuous_decodnig": False,
        "spkr": spkr_id,
        "lang": spkr_lang,
        "ctxt": spkr_ctxt
    }
    ws.send(json.dumps(start_msg))
    res_msg = ws.recv()
    #print(f"ws: {res_msg}")
        
    # (2) send audio data 
    ws.send(bytes(audio_data))
      
    # (3) send end msg
    end_msg = {"signal":"end"}
    ws.send(json.dumps(end_msg))
    res_msg = ws.recv()
    # print(f"ws: {res_msg}")
    
    # -- close websocket --
    ws.close()
    
    nbest = json.loads(res_msg)["nbest"]
    final_sent = json.loads(nbest)[0]["sentence"]
    return final_sent

# ---------------------------------------------------------------------
def tts_result(text, lang, sex):
    result = None
    try:
        result = requests.get(
            tts_url,
            params={
                "text": text,
                "language": lang,
                "sex": sex
            })
    except Exception as e:
        st.toast(f"Error in generationg speech")
    finally:
        return result
    
# ---------------------------------------------------------------------
def run_asr(audio, spkr_lang, version="densper1"):
    return run_asr_densper1(audio, spkr_lang) if version == "densper1"  else run_asr_densper2(audio, spkr_lang)
