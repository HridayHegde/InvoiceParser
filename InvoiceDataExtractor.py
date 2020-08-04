import os
from pathlib import Path
from CustomPackages import TabulaModule as TM
from CustomPackages import OCRModule as OCRM
import json
import re

originfolder = "./PDFInvoices"
destfolder = "./ConvertedInvoices/"
requiredfile = "requiredFields.json"
def main():
    #region Main
    file_set = []
    for file in os.listdir(originfolder):
        if file.endswith(".pdf") or file.endswith(".PDF"):
            file_set.append(os.path.join(originfolder, file))

    print(file_set)


    for f in file_set:
        try:
            os.mkdir(destfolder+Path(f).stem)
            
        except OSError as e:
            print(e)
        try:
            os.mkdir(destfolder+Path(f).stem+'/temp')
        except OSError as e:
            print(e)

        reqfile = open(requiredfile) 
        data = json.load(reqfile)
        for freg in data['invoices']:    
            if re.compile(freg['name']).search(Path(f).stem):
                if freg['setting'] == "Tabula":
                    print("--------Tabula Method------")
                    TM.ExtractImages(f)#ExtractImages from PDF

                    barcode_data = TM.ParseQRCode(f)#Scan For QRCOde and output to file
                    
                    df = TM.GenerateCSV(f)
                    

                    TM.parseReqDataTabula(f,destfolder+Path(f).stem+'/'+Path(f).stem+'.csv',barcode_data,df)
                elif freg['setting'] == "OCR":
                    print("-------OCR Method------")
                    ocrtext = OCRM.GenerateOCR(f)

                    qrdata =OCRM.ParseOCR_QRcode(f)
                    
                    OCRM.ParseOCR(f,ocrtext,barcodedata=qrdata)

                
        #os.remove(f)

    #region end Main
main()