import json
import tabula
import os
from pathlib import Path
import fitz
import zxing

import io
from PIL import Image

import numpy as np

import pandas as pd
import csv
import re

def GenerateCSV(f):
    print("Generating CSV....")
    df = tabula.read_pdf(f,stream=True,pandas_options={'header': None})

    df = df[0]
                
    df.to_csv(('./ConvertedInvoices/'+Path(f).stem+'/'+Path(f).stem+'.csv'), encoding='utf-8')
    return df

def ParseQRCode(pdfpath):
    print("Parsing QR Code by image extraction....")
    file_set1 = []
    barcodeexists = False
    for file in os.listdir("./COnvertedInvoices/"+Path(pdfpath).stem+"/temp"):
        file_set1.append(os.path.join("./COnvertedInvoices/"+Path(pdfpath).stem+"/temp", file))

    for f in file_set1:
        print(f)
        
        reader = zxing.BarCodeReader()
        barcode = reader.decode(f)
        print(barcode.raw)
      
        print("QR Data : "+barcode.raw)
        if barcode:
            barcodeexists = True
            file_object = open('./ConvertedInvoices/'+Path(pdfpath).stem+'/qrdata.txt', 'a')
            file_object.write(barcode.raw)
            file_object.close()

    if barcodeexists:
        return barcode.raw
    else:
        return "0"


def ExtractImages(filename):
    print("Extracting Images.....")
    
    doc = fitz.open(filename)
    for i in range(len(doc)):
        for img in doc.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:       # this is GRAY or RGB
                pix.writePNG("./ConvertedInvoices/"+Path(filename).stem+"/temp/p%s-%s.png" % (i, xref))
            else:               # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.writePNG("./ConvertedInvoices/"+Path(filename).stem+"/temp/p%s-%s.png" % (i, xref))
                pix1 = None
            pix = None

def parseReqDataTabula(filepath,pathtocsv,barcodedata,dataframe,reqfieldsfile = "requiredFields.json"):#Parses and writes the CSV according to JSON Settings
    print("Parsing Tabula Data......")
    
    writedict = {}

    print("PARSING DATAFRAME")
    df = dataframe
    f = open(reqfieldsfile) 
    data = json.load(f)
    fieldnames = ['PDF Name']
    for x in data['invoices']:
        if re.compile(x['name']).search(Path(filepath).stem):
            for y in x['field']:
                if y:
                    fieldnames.append(y['FinalOutputField'])
    fieldnames.append('QR Code')
    #region CSV Setup
    fileexists = os.path.isfile("./ConvertedInvoices/"+Path(filepath).stem+"/"+Path(filepath).stem+"_RequiredFiledsOnly.csv")
    csv_file = open("./ConvertedInvoices/"+Path(filepath).stem+"/"+Path(filepath).stem+"_RequiredFiledsOnly.csv",mode='a')
    
    writer = csv.DictWriter(csv_file,fieldnames)
    if not fileexists:
        writer.writeheader()
    #region end CSV SETUP
    writedict["PDF Name"] = str(Path(filepath).stem)

    for freg in data['invoices']:
        print('ITTTTTTETETET ::: '+freg['name'])
        if re.compile(freg['name']).search(Path(filepath).stem):
            for i in freg['field']:
                name = i['datafieldname']
                pos = i['position']
                z = int(i["NoofSkips"])
                fout = i["FinalOutputField"]
                a = np.where(df.values == name)
                res = [x[0] for x in a]
                dfpos = res
                
                if pos == "r":
                    if df.iat[dfpos[0],(dfpos[1]+1)] == "" or pd.isnull(df.iat[dfpos[0],(dfpos[1]+1)]) or z !=0:
                        while df.iat[dfpos[0],(dfpos[1]+1)] == "" or pd.isnull(df.iat[dfpos[0],(dfpos[1]+1)]) or z !=0:
                            dfpos[1] = (dfpos[1]+1)
                            print("NEW POS:::"+str(dfpos[1]))
                            if df.iat[dfpos[0],(dfpos[1]+1)] != "" and z!=0:
                                z = z-1
                                dfpos[1] = (dfpos[1]+1)
                        
                        print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data
                        #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                        writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])

                    else:
                        print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data  
                        #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                        writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])

                elif pos == "rd":
                    dfpos[0] = dfpos[0]+1
                    print("RD NEW POS ::: "+str(dfpos))
                    print("RD NEW POS IF EMPTY::: "+str(dfpos[1]+1))
                    print("RD NEW POS IF EMPty Data::: "+str(df.iat[dfpos[0],dfpos[1]+1]))
                    if df.iat[dfpos[0],(dfpos[1]+1)] == "" or pd.isnull(df.iat[dfpos[0],(dfpos[1]+1)]) or z !=0:
                        while df.iat[dfpos[0],(dfpos[1]+1)] == "" or pd.isnull(df.iat[dfpos[0],(dfpos[1]+1)]) or z !=0:
                            dfpos[1] = (dfpos[1]+1)
                            print("NEW POS:::"+str(dfpos[1]))
                            if df.iat[dfpos[0],(dfpos[1]+1)] != "" and z!=0:
                                z = z-1
                                dfpos[1] = (dfpos[1]+1)
                        
                        print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data
                        #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                        writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])

                    else:
                        print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data  
                        #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                        writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])
                        
                elif pos == "d":
                    dfpos[0] = dfpos[0]+1
                    print(name +" Data: "+df.iat[dfpos[0],dfpos[1]])#Final Data
                    writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                    writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])
                
                elif pos == "ru":
                    dfpos[0] = dfpos[0]-1
                    if df.iat[dfpos[0],(dfpos[1]+1)] == "" or pd.isnull(df.iat[dfpos[0],(dfpos[1]+1)]) or z !=0:
                        while df.iat[dfpos[0],(dfpos[1]+1)] == "" or pd.isnull(df.iat[dfpos[0],(dfpos[1]+1)]) or z !=0:
                            dfpos[1] = (dfpos[1]+1)
                            print("NEW POS:::"+str(dfpos[1]))
                            if df.iat[dfpos[0],(dfpos[1]+1)] != "" and z!=0:
                                z = z-1
                                dfpos[1] = (dfpos[1]+1)

                        
                        print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data
                        #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                        writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])

                    else:
                        print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data  
                        #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                        writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])
                else :
                    print("Position not specified")
            #writer.writerow({'fields':'QRCode','data':barcode_data})
            
            writedict['QR Code'] = barcodedata


    print(writedict)
    if not not writedict  :
        writer.writerow(writedict)
    else:
        print("Error no template for file in requiredFields.json")
    csv_file.close()
    
