import os
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import time
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from pikepdf import Pdf

# -------------------------------------------------
page_title = "Bill Reader - OCR"

st.set_page_config(
    page_title = page_title,
    page_icon="🎁",
    layout="wide",
    menu_items=None
)

temp_dir = "./pdfs"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
ocr_model = ocr_predictor("db_resnet50", "crnn_vgg16_bn", \
    pretrained=True).cuda() # for gpu inference 

if 'pdf_file' not in st.session_state:
    st.session_state.pdf_file = ""

# -------------------------------------------------
def ocr(item):
    result = ocr_model(item)
    json_output = result.export()
    return result, json_output

def read_line_data(json_output):
    # Show the results
    whole_words = []
    per_line_words = []
    for block in json_output["pages"][0]["blocks"]:
        for line in block["lines"]:
            line_words = []
            for word in line["words"]:
                whole_words.append(word["value"])
                line_words.append(word["value"])
            per_line_words.append(line_words)
    #print(f"{per_line_words}")
    return per_line_words

def bill_from_humana(line_words, line_cnt):
    claim_data = []
    line_max = len(line_words)
    claim_number = ''
    patient_name = ''
    claim_totals = ''
    for i in range(line_cnt, line_max):
        words = line_words[i]
        line = ' '.join(words).lower()
        line = line.replace(":", "")
        #print(f'{line}')
        if ('claim' in line and 'number' in line):
            for j in range(i, line_max):
                for word in line_words[j]:
                    if len(word)==15 and word.isdigit():
                       claim_number = word; break
                if claim_number or j>i+10: break
        if ('patient' in line and 'name' in line):
            temp_ = line.replace('patient', '').replace('name', '')
            patient_name = temp_.strip()            
        if 'claim totals' in line:
            for j in range(i, line_max):
                words = line_words[j]
                line = ' '.join(words).lower()
                if 'estimated' in line:
                    claim_totals = line_words[j-1][0]
                    break
                if j>i+10: break
        if claim_number and claim_totals:
            claim_ = {'claim_number':claim_number, \
                'patient_name':patient_name, \
                'claim_totals':claim_totals}
            claim_data.append(claim_)
            claim_number = ''
            claim_totals = ''
    return claim_data

def extract_bill_info(line_words):
    bill_info = {}
    ins_company = ''
    claim_data = []
    line_cnt = 0
    for words in line_words:
        line = ' '.join(words)
        line_cnt += 1
        # -- (1) insurance company 
        if 'Humana.' in line:
            ins_company = 'Humana'
            claim_data = bill_from_humana(line_words, line_cnt)
        if line_cnt>10: break

    bill_info['insurance'] = ins_company
    bill_info['claim_data'] = claim_data
    return bill_info

# -------------------------------------------------
if __name__ == "__main__":
    st.title(page_title)
        
    selection, output = st.columns((0.5, 0.5))
    with selection:
        pdf_file = st.file_uploader("Upload PDF file", type=('pdf'))
        if pdf_file:
            binary_data = pdf_file.getvalue()
            pdf_viewer(input=binary_data, width=700)
            st.session_state.pdf_file = pdf_file

    with output:
        call_server = st.button("Run OCR")
        #st.divider()
        if call_server:
            if st.session_state.pdf_file:
                scanned_pdf = st.session_state.pdf_file
                start_time = time.time()
                pdf = Pdf.open(scanned_pdf)
                elapsed_time = time.time() - start_time 
                #st.markdown(f"** (loading {scanned_pdf}) :=> {elapsed_time:.2f} seconds") 
                #st.markdown(f"** loading pdf :=> {elapsed_time:.2f} seconds") 

                for i, page in enumerate(pdf.pages):
                    start_time = time.time()
                    dst = Pdf.new()
                    dst.pages.append(page)
                    part_fn = temp_dir+'/page_'+str(i+1)+'.pdf'
                    dst.save(f'{part_fn}')
                    img_doc = DocumentFile.from_pdf(part_fn)
                    result, json_data = ocr(img_doc)
                    elapsed_time = time.time() - start_time 
                    st.markdown(f"** ocr reading {part_fn} :=> {elapsed_time:.2f} seconds")
                    line_data = read_line_data(json_data)
                    with st.expander("See - ocr data"):
                        st.markdown(f"{line_data}")
                    bill_info = extract_bill_info(line_data)
                    #st.markdown(f"** extract bill info")
                    with st.expander("See - bill info"):
                        st.markdown(f"{bill_info}")
                    