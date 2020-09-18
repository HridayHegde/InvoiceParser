import os
from pathlib import Path

#from CustomPackages 

from CustomPackages import TabulaModule as TM
from CustomPackages import OCRModule as OCRM
from CustomPackages import jwtdecoding as jwtD

import json
import re

from datetime import datetime

import shutil


originfolder = "./PDFInvoices"
destfolder = "./ConvertedInvoices/"
requiredfile = "requiredFields.json"

def clearoutputs():
    for file in os.listdir("./FinalOutputs"):
        os.remove("./FinalOutputs/"+file)
def main():
    print("STARTING MAIN ::::  ")
    #region Main
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

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
                    irnnumber = ""
                    barcode_data = TM.ParseQRCode(f)#Scan For QRCOde and output to file
                    print("BARCODE DATA :::::: "+str(barcode_data)+" :::::")
                    if barcode_data != "":
                        qrextracteddata = jwtD.jwtdecode(barcode_data,"requiredFields.json",f)
                    else:
                        qrextracteddata = {}
                    print("Irn NUMBER    : :: :  "+str(irnnumber))
                    #irnnumber = jwtD.jwtdecode(barcode_data)
                    print("Irn NUMBER    : :: :  "+str(irnnumber))
                    df = TM.GenerateCSV(f)
                    

                    TM.parseReqDataTabula(dt_string,f,destfolder+Path(f).stem+'/'+Path(f).stem+'.csv',qrextracteddata,df)
                elif freg['setting'] == "OCR":
                    print("-------OCR Method------")
                    ocrtext = OCRM.GenerateOCR(f)
                    irnnumber = ""
                    qrdata =OCRM.ParseOCR_QRcode(f)
                    print("BARCODE DATA :::::: "+str(qrdata)+" :::::")
                    if qrdata != "":
                        qrextracteddata = jwtD.jwtdecode(qrdata,"requiredFields.json",f)
                    else:
                        qrextracteddata = {}
                    print("Irn NUMBER    : :: :  "+str(irnnumber))
                    
                    OCRM.ParseOCR(dt_string,f,ocrtext,barcodedata=qrextracteddata)
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
    try:
        shutil.rmtree("./ConvertedInvoices")
    except OSError as e:
        print(e)
    try:
        os.mkdir("./ConvertedInvoices")
    except OSError as e:
        print(e)
    
    return True
    #region end Main

