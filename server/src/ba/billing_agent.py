#import os
import json
import base64
from io import BytesIO
from pikepdf import Pdf
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from ba.ins_company import InsCompany

# -------------------------------------------------
temp_dir = '../pdfs'
ocr_model = ocr_predictor("db_resnet50", "crnn_vgg16_bn", \
    pretrained=True).cuda() # for gpu inference 
ins = InsCompany()
# -------------------------------------------------

class BillingAgent:
    def __init__(self):
        print(f' * init ')
    
    # -----------------------------------------------    
    def ocr(self, item):
        result = ocr_model(item)
        json_output = result.export()
        return result, json_output

    def read_line_data(self, json_output):
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
    # -----------------------------------------------

    def run(self, user_name, pdf_base64):
        print(f' * run - {user_name:} ')
        # save pdf_data 
        pdf_data = base64.b64decode(pdf_base64)
        pdf_bytes = BytesIO(pdf_data)
        #import pdb; pdb.set_trace()
        pdf_fn = temp_dir+'/'+user_name+'.pdf'
        with open(pdf_fn, "wb") as f:
            f.write(pdf_bytes.getbuffer())

        pdf = Pdf.open(pdf_fn)
        ocr_data = []
        for i, page in enumerate(pdf.pages):
            dst = Pdf.new()
            dst.pages.append(page)
            page_fn = temp_dir+'/'+user_name+'_'+str(i+1)+'.pdf'
            print(f'** page - {page_fn}')
            dst.save(f'{page_fn}')
            img_doc = DocumentFile.from_pdf(page_fn)
            result, json_data = self.ocr(img_doc)
            line_data = self.read_line_data(json_data)
            #eob_info = ins.extract_eob_info(line_data)
            #ocr_data.append(eob_info)
            ocr_data.append(line_data)
        return ocr_data
