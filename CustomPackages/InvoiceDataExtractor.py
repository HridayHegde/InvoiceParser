import os
from pathlib import Path

#from CustomPackages 

from CustomPackages import TabulaModule as TM
from CustomPackages import OCRModule as OCRM
from CustomPackages import jwtdecoding as jwtD

import json
import re

import shutil


originfolder = "./PDFInvoices"
destfolder = "./ConvertedInvoices/"
requiredfile = "requiredFields.json"

def clearoutputs():
    for file in os.listdir("./FinalOutputs"):
        os.remove("./FinalOutputs/"+file)
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
            print(":::::::::::::::::::"+freg['name']+"::::::::::::::::::::::::::::::::")
            if re.compile(freg['name']).search(Path(f).stem):
                if freg['setting'] == "Tabula":
                    print("--------Tabula Method------")
                    
                    TM.ExtractImages(f)#ExtractImages from PDF

                    barcode_data = TM.ParseQRCode(f)#Scan For QRCOde and output to file
                    if barcode_data == "":
                        irnnumber = jwtD.jwtdecode(barcode_data)
                    else:
                        irnnumber = ""
                    print("Irn NUMBER    : :: :  "+str(irnnumber))
                    irnnumber = jwtD.jwtdecode(barcode_data)
                    print("Irn NUMBER    : :: :  "+str(irnnumber))
                    df = TM.GenerateCSV(f)
                    

                    TM.parseReqDataTabula(f,destfolder+Path(f).stem+'/'+Path(f).stem+'.csv',irnnumber,df)
                elif freg['setting'] == "OCR":
                    print("-------OCR Method------")
                    ocrtext = OCRM.GenerateOCR(f)

                    qrdata =OCRM.ParseOCR_QRcode(f)
                    if qrdata == "":
                        irnnumber = jwtD.jwtdecode(qrdata)
                    else:
                        irnnumber = ""
                    print("Irn NUMBER    : :: :  "+str(irnnumber))
                    
                    OCRM.ParseOCR(f,ocrtext,barcodedata=irnnumber)
        os.remove(f)

    shutil.make_archive("./ZipOutput/output_zip", 'zip', "./FinalOutputs/")
    try:
        shutil.rmtree("./PDFInvoices")
    except OSError as e:
        print(e)
    try:
        shutil.rmtree("./ZipOutput/output_zip")
    except OSError as e:
        print(e)
    try:
        os.mkdir("./ZipOutput/output_zip")
    except OSError as e:
        print(e)
    try:
        os.mkdir("./PDFInvoices")
    except OSError as e:
        print(e)
    clearoutputs()
    shutil.rmtree("./ConvertedInvoices")
    os.mkdir("./ConvertedInvoices")

    #region end Main
#main()
