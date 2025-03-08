import streamlit as st
import streamlit.components.v1 as components
import requests
import base64
from io import BytesIO
from datetime import datetime
import numpy as np
import json
import librosa
from websockets.sync.client import connect
from scipy.io.wavfile import write as audio_write

from src.stt import run_asr_densper1, run_asr_densper2

if 'input_type' not in st.session_state:
    st.session_state.input_type = "realtime"

if 'input_lang' not in st.session_state:
    st.session_state.input_lang = "ko"

if 'stt_version' not in st.session_state:
    st.session_state.stt_version = "densper2"

if 'v1_result' not in st.session_state:
    st.session_state.v1_result = ""

if 'v2_result' not in st.session_state:
    st.session_state.v2_result = ""

if 'tts_lang' not in st.session_state:
    st.session_state.tts_lang = "ko"

if 'tts_gender' not in st.session_state:
    st.session_state.tts_gender = "male"

if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
    
st.set_page_config(
    page_title="NDAI - STT, TTS", 
    page_icon="🔊", 
    layout="wide",
    # initial_sidebar_state="collapsed",
    menu_items=None)

# HTML/JS를 통한 명시적 권한 요청
components.html("""
<script>
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(function(stream) {
        console.log('Permission granted');
    })
    .catch(function(err) {
        console.log('Permission denied');
    });
</script>
""", height=0)

# 덴스퍼 1 서버
# densper1_url = "http://175.209.148.123:8000/transcribe"

# 덴스퍼 2 서버
lang_map = {
    "ko": "ws://175.209.148.123:20010",
    "en": "ws://175.209.148.123:20011",
    "cn": "ws://192.168.1.219:20012",
    "ml3": "ws://192.168.1.219:20101"
}

tts_url = "http://192.168.1.220:20300/generate-audio"


# (STT - Densper2) ----------------------------------------------------
spkr_id = "dcai_web_demo"
spkr_ctxt = ""
target_sr = 16000
max_int16 = 2**15

def transcribe(audio):
    '''
    Preprocessing raw mircrophone audio data
    '''
    sr, y = audio
    
    # Convert to mono if stereo
    if y.ndim > 1:
        y = y.mean(axis=1)
        
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))

    return run_asr({"sampling_rate": sr, "raw": y})


# ---------------------------------------------------------------------
def tts_result():
    result = None
    try:
        result = requests.get(
            tts_url,
            params={
                "text": st.session_state.input_text,
                "language": st.session_state.tts_lang,
                "sex": st.session_state.tts_gender
            })
    except Exception as e:
        st.toast(f"Error in generationg speech")
    finally:
        return result

# ---------------------------------------------------------------------
def run_asr(audio):
    return run_asr_densper1(audio, st.session_state.input_lang) if st.session_state.stt_version == "densper1"  else run_asr_densper2(audio, st.session_state.input_lang)

if __name__ == "__main__":
    # (STT - View) ----------------------------------------------------

    with st.expander("🎈 데모페이지에서 마이크/웹캠 사용이 안되는 경우"):
        ref_image_section,info_section = st.columns(2)
        with ref_image_section:
            st.image("./data/refs/howtoinsecure.png")
        with info_section:
            st.markdown("""
                1. 브라우저 주소창에 **chrome://flags/#unsafely-treat-insecure-origin-as-secure** 열기
                2. Insecure origins treated as secure 섹션 찾기
                3. 우측 선택지를 사용 정지 -> 사용 가능 으로 변경
                4. 좌측에 데모 페이지 주소 (**http://192.168.1.55:8502**) 입력
                5. 브라우저 종료 후 다시 시작될 때부터 적용됨
            """)

    with st.container(border=True):
        control_section, result_section = st.columns(2)

        with result_section:
            st.header("Result")

        with control_section:
            st.header("STT")
            st.selectbox("Select a file to upload", ["densper1", "densper2"], key="stt_version")
            #st.selectbox("Select a file to upload", ["densper2"], key="stt_version")
            file_type_seceion, stt_lang_select_section = st.columns(2)
            
            with file_type_seceion:
                st.radio(
                    "Select a file to upload", 
                    options=["realtime", "audio_file"],
                    #options=["realtime"],
                    key="input_type")
            with stt_lang_select_section:
                st.radio(
                    "Select language",
                    options=list(lang_map.keys()),
                    captions=["한국어", "영어", "중국어", "다국어"],
                    horizontal=True,
                    key="input_lang")
            audio_value = st.audio_input("Record a voice message")
            uploaded_audio = st.file_uploader("Upload a file", type=["mp3", "wav"])
            
            if st.button("Transcribe"):
                if audio_value and st.session_state.input_type == "realtime":
                    with result_section:
                        st.markdown("Captured audio")
                        st.audio(audio_value)
                with result_section:
                    with st.spinner("Transcribing..."):
                        start = datetime.now()
                        stt_result = run_asr(
                            audio_value if st.session_state.input_type == "realtime" and audio_value is not None 
                            else uploaded_audio if st.session_state.input_type == "audio_file" and uploaded_audio is not None 
                            else None)
                        st.markdown(f"Transcribed in {datetime.now() - start}")
                        if st.session_state.stt_version == "densper1":
                            st.session_state.v1_result = stt_result
                        else:
                            st.session_state.v2_result = stt_result
        
            with result_section:
                #st.markdown("Densper 1 STT Result")
                #st.code(st.session_state.v1_result)
                #st.download_button('Download Densper1 Result', st.session_state.v1_result)
                st.markdown("STT Result")
                st.code(st.session_state.v2_result)
                st.download_button('Download Result', st.session_state.v2_result)

    # (TTS - View) ----------------------------------------------------
    with st.container(border=True):
        control_section, result_section = st.columns(2)

        with result_section:
            st.header("Result")

        with control_section:
            st.header("TTS")
            tts_gender_section, tts_lang_select_section = st.columns(2)
            with tts_gender_section:
                st.radio(
                    "Seelect speaker",
                    options=["male", "female"],
                    key="tts_gender"
                )
            
            with tts_lang_select_section:
                st.radio(
                    "Select language",
                    options=list(lang_map.keys()),
                    captions=["한국어", "영어", "중국어", "다국어"],
                    horizontal=True,
                    key="tts_lang")
            st.text_area("tts text", key="input_text", placeholder="Enter text to convert to speech")

            if st.button("Text to Speech"):
                with result_section:
                    with st.spinner("Generating speech..."):
                        start = datetime.now()
                        tts_result = tts_result()
                        st.markdown(f"TTS generated in {datetime.now() - start}")
                        st.audio(tts_result.content, format="audio/wav")
                        