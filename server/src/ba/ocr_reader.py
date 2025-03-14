from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from pikepdf import Pdf
import json

class EobInfo:
    def __init__(self, ins_company):
        self.ins_company = ins_company
    
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
        

class OcrReader:
    def __init__(self):
        self.data_path = '../data'
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        self.ocr_model = ocr_predictor("db_resnet50", "crnn_vgg16_bn", \
            pretrained=True).cuda() # for gpu inference 
        
    def ocr(self, img_doc):
        result = ocr_model(item)
        json_output = result.export()
        return result, json_output

    def run(self, user, scanned_pdf):
        print(f' - ')
        pdf = Pdf.open(scanned_pdf)
        pdf_data = []
        for i, page in enumerate(pdf.pages):
            dst = Pdf.new()
            dst.pages.append(page)
            part_fn = self.data_path+'/'+user+'_'+str(i+1)+'.pdf'
            dst.save(f'{part_fn}')
            img_doc = DocumentFile.from_pdf(part_fn)
            result, json_data = self.ocr(img_doc)
            line_data = read_line_data(json_data)
            #bill_info = extract_bill_info(line_data)
            pdf_data.append(line_data)
            
        return pdf_data