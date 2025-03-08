import os
import numpy as np
from PIL import Image
import streamlit as st
import cv2
from openai import OpenAI
import base64 

# -------------------------------------------------
page_title = "Invoice Reader"

st.set_page_config(
    page_title = page_title,
    page_icon="🎁",
    layout="wide",
    menu_items=None
)

# -------------------------------------------------
if 'demo_file_path' not in st.session_state:
    st.session_state.demo_file_path = "./data/invoice"
if 'bright_ratio' not in st.session_state:
    st.session_state.bright_ratio = 1.0
if 'result' not in st.session_state:
    st.session_state.result = ""

# -------------------------------------------------
def valid_file_extension(file_name):
    return True if file_name.split('.')[-1] in ['jpg', 'png', 'jpeg',] else False

def img_convert(img: np.array) -> np.array:
    if isinstance(img, Image.Image):
        img = np.array(img)
    img = np.clip((img * st.session_state.bright_ratio), 0, 255).astype(np.uint8)
    return img

def read_dcm(file_path):
    dcm = pydicom.dcmread(file_path, force=True,)
    return img_convert(dcm.pixel_array)

def read_image(file_path):
    return img_convert(cv2.imread(file_path))
    #with open(file_path, "rb") as image_file:
    #    return base64.b64encode(image_file.read()).decode("utf-8")

def load_image(file_path):
    if isinstance(file_path, st.runtime.uploaded_file_manager.UploadedFile) or\
        isinstance(file_path, np.ndarray):
        return file_path
    elif file_path.endswith(".dcm"):
        return read_dcm(file_path)
    else:
        return read_image(file_path)


demo_pics = [pic for pic in os.listdir(st.session_state.demo_file_path) if valid_file_extension(pic)]

# -------------------------------------------------
client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    #return base64.b64encode(image_obj).decode("utf-8")

# add prompt - 2025/01/13, Kyi 
def openai_api(prompt, image_obj):
    #base64_image = encode_image(image_obj)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_obj}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0]

# -------------------------------------------------

if __name__ == "__main__":
    st.title(page_title)
        
    _, selection, output = st.columns((0.05, 0.25, 0.7))
    with selection:
        st.markdown(
            body="""
            <style>
            div[role="radiogroup"] div[data-testid="stMarkdownContainer"]:has(p){ visibility: hidden; height: 0px; }
            </style>
            """,
            unsafe_allow_html=True)
        radio_list = demo_pics + ["Upload a file"]
        st.radio(
            "Select a file to upload", 
            radio_list,
            captions=radio_list,
            format_func= lambda x: f"demo {radio_list.index(x)+1}" if radio_list.index(x) < len(demo_pics) else x,
            key="demo_file_name")
        uploaded_image = st.file_uploader("Upload a file", type=["jpg", "png", "jpeg"])

    with output:
        if uploaded_image is not None and st.session_state.demo_file_name == "Upload a file":
            selected_image = load_image(uploaded_image)
            base64_image = base64.b64encode(uploaded_image.read()).decode("utf-8")
        elif st.session_state.demo_file_name != "Upload a file":
            selected_image = load_image(os.path.join(st.session_state.demo_file_path, st.session_state.demo_file_name))
            base64_image = encode_image(os.path.join(st.session_state.demo_file_path, st.session_state.demo_file_name))
        else:
            st.warning("Please Upload Image.")
            st.stop()

        observe_image = st.image(
            image=selected_image,
            width=760,)
        
        st.divider()
        #prompt = st.text_input("Command Prompt", "From the invoice image, what is the total cost?")
        #prompt = st.text_area(
        #    "Command Prompt: ", 
        #    "I received an invoice from insurance company. And I want to know following items: \n\n"
        #    "1. Name of the patient. \n"
        #    "2. Date of birth. \n"
        #    "3. Date of service. \n"
        #    "4. ADA code. \n"
        #    "5. Billing amount. \n"
        #    "6. Total paid amount. \n",
        #    250
        #)
        prompt = st.text_area(
                "Command Prompt: ",
                "From the invoice image of an insurance company, I want to know following items: \n\n"
                "1. Name of the patient. \n"
                "2. Total paid amount.\n",
                150
        )
        call_server = st.button("Run Inference")

    #st.divider()

    if call_server:
        # Your inference code goes here...
        if isinstance(selected_image, np.ndarray):
            selected_image = open(os.path.join(st.session_state.demo_file_path, st.session_state.demo_file_name), "rb")
        with st.spinner("분석 중..."):
            #response = requests.post("http://localhost:8005/predict", files={"file": selected_image})
            response = openai_api(prompt, base64_image)
            #st.session_state.result = f"hi.."
            st.session_state.result = f"{response}"

    result_container = st.columns(2)
    with result_container[0]:
        st.markdown("### Result")
        st.markdown(st.session_state.result)
    
