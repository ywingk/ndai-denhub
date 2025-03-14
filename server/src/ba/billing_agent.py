#import os
import json
import base64
from io import BytesIO
from pikepdf import Pdf
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# -------------------------------------------------
temp_dir = '../pdfs'
ocr_model = ocr_predictor("db_resnet50", "crnn_vgg16_bn", \
    pretrained=True).cuda() # for gpu inference 
# -------------------------------------------------

class BillingAgent:
    def __init__(self):
        print(f' * init ')
        
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

    def bill_from_humana(self, line_words, line_cnt):
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

    def extract_bill_info(self, line_words):
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
                claim_data = self.bill_from_humana(line_words, line_cnt)
            if line_cnt>10: break

        bill_info['insurance'] = ins_company
        bill_info['claim_data'] = claim_data
        return bill_info


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
            bill_info = self.extract_bill_info(line_data)
            ocr_data.append(bill_info)            
        return ocr_data
