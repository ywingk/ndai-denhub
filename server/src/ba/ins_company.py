#

class InsCompany:
    def __init__(self):
        print(f' * init InsCompany ')
    
    def extract_eob_info(self, line_words):
        bill_info = {}
        ins_company = ''
        eob_data = []
        line_cnt = 0
        for words in line_words:
            line = ' '.join(words)
            line_cnt += 1
            # -- (1) insurance company 
            if 'Humana.' in line:
                ins_company = 'Humana'
                eob_data = self.eob_humana(line_words, line_cnt)
            if line_cnt>10: break

        bill_info['insurance'] = ins_company
        bill_info['eob_data'] = eob_data
        return bill_info

    def eob_humana(self, line_words, line_cnt):
        eob_data = []
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
                eob_data.append(claim_)
                claim_number = ''
                claim_totals = ''
        return eob_data

        