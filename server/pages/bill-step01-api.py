import os
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import time
import base64
import requests
import json
from src.ba.ins_company import InsCompany

# -------------------------------------------------
if os.environ['USER'] == 'kyi':
    denapi_url = "http://0.0.0.0:30005/denapi/billing-agent/"
else:
    denapi_url = "https://ndai.ddns.net/denapi/billing-agent/"

ins = InsCompany()

# -------------------------------------------------
page_title = "Bill Reader - API"

st.set_page_config(
    page_title = page_title,
    page_icon="🎁",
    layout="wide",
    menu_items=None
)

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'pdf_file' not in st.session_state:
    st.session_state.pdf_file = ""
    
# -------------------------------------------------
def run_ba_api(user_name, pdf_data):
    # base64 encode 
    pdf_base64 = base64.b64encode(pdf_data.getvalue()).decode("utf-8")
    payload = {
        "user_name": user_name,
        "pdf_base64": pdf_base64
        }
    # request 
    response = requests.request(
        method="POST",
        url=denapi_url,
        headers={"Content-Type": "application/json"},
        json=payload
    )
    print(f'** response: {response.text:}')
    result = json.loads(response.text)
    #import pdb; pdb.set_trace()
    result = json.loads(result)
    return result
    
# -------------------------------------------------
if __name__ == "__main__":
    st.title(page_title)
        
    selection, output = st.columns((0.5, 0.5))
    with selection:
        
        user_name = st.text_input("User Name:", "test")
        if user_name:
            st.session_state.user_name = user_name
        pdf_file = st.file_uploader("Upload PDF file", type=('pdf'))
        if pdf_file:
            binary_data = pdf_file.getvalue()
            pdf_viewer(input=binary_data, width=700)
            st.session_state.pdf_file = pdf_file

    with output:
        if st.session_state.pdf_file and st.session_state.user_name:
            pdf_data = st.session_state.pdf_file
            user_name = st.session_state.user_name
            start_time = time.time()
            result = run_ba_api(user_name, pdf_data)
            elapsed_time = time.time() - start_time 
            st.markdown(f"** Billing Agent - API Response: ({elapsed_time:.2f} seconds)")
            #import pdb; pdb.set_trace()
            for item in result:
                with st.expander("ocr data"):
                    st.markdown(f"{item}")
                eob_info = ins.extract_eob_info(item)
                st.markdown(f"- EOB Info: {eob_info}")
                st.markdown(f"- TODO: generate mysql script for claim processing...")
