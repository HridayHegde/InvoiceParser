import json
import tabula
import os
from pathlib import Path
import fitz
import zxing

import pyzbar
#import qrtools.qrtools as rqr
import io
from PIL import Image

import numpy as np

import pandas as pd
import csv
import re

from CustomPackages import DatabaseInteraction as DI

def GenerateCSV(f):
    print("....Generating CSV....")
    df = tabula.read_pdf(f,stream=True,pandas_options={'header': None})

    df = df[0]
                
    df.to_csv(('./ConvertedInvoices/'+Path(f).stem+'/'+Path(f).stem+'.csv'), encoding='utf-8')
    return df

def GenerateCSVTemplate(f):
    print("....Generating TEMPLATE CSV....")
    df = tabula.read_pdf(f,stream=True,pandas_options={'header': None})

    df = df[0]
                
    df.to_csv(('./TemplateGenerator/Output/'+Path(f).stem+'.csv'), encoding='utf-8')
    return df
def ParseQRCode(pdfpath):
    print("....Parsing QR Code by image extraction....")
    
    file_set1 = []
    barcodeexists = False
    for file in os.listdir("./ConvertedInvoices/"+Path(pdfpath).stem+"/temp"):
        file_set1.append(os.path.join("./ConvertedInvoices/"+Path(pdfpath).stem+"/temp", file))

    for f in file_set1:
        print(f)
        
        
        #qrreader = rqr.QR()
        #qrreader.decode(f)
        reader = zxing.BarCodeReader()
        try:
            barcode = reader.decode(f)
        except OSError as e:
            print("CHECK FOR ERRORS")
            print(e) 
         #qrreader.data#
        
        #print(barcode.raw)
      
        #print("QR Data : "+barcode.raw)
        
        if barcode is not None:
            print(barcode)
            barcodeexists = True
            file_object = open('./ConvertedInvoices/'+Path(pdfpath).stem+'/qrdata.txt', 'a')
            file_object.write(barcode.raw)
            file_object.close()
            return barcode.raw
        else:
            return ""

    if barcodeexists:
        try:
            return barcode.raw
        except:
            return ""
    else:
        return ""


def ExtractImages(filename):
    print("....Extracting Images.....")
    
    doc = fitz.open(filename)
    for i in range(len(doc)):
        for img in doc.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:       # this is GRAY or RGB
                pix.writePNG("./ConvertedInvoices/"+Path(filename).stem+"/temp/p%s.png" % (i))
            else:               # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.writePNG("./ConvertedInvoices/"+Path(filename).stem+"/temp/p%s.png" % (i))
                pix1 = None
            pix = None

def parseReqDataTabula(datetime,filepath,pathtocsv,barcodedata,dataframe,reqfieldsfile = "requiredFields.json"):#Parses and writes the CSV according to JSON Settings
    print(".....Parsing Tabula Data......")
    
    writedict = {}

    print("....PARSING DATAFRAME....")
    df = dataframe
    f = open(reqfieldsfile) 
    data = json.load(f)
    fieldnames = ['PDF Name']
    for x in data['invoices']:
        if re.compile(x['name']).search(Path(filepath).stem):
            for y in x['field']:
                if y:
                    fieldnames.append(y['FinalOutputField'])
    
    for x in data['invoices']:
        if re.compile(x['name']).search(Path(filepath).stem):
            if 'qrdata' in x:
                for y in x['qrdata']:
                    if y:
                        fieldnames.append(y["visualname"])
    
    print("FieldNamesAre : : : :: :  : : :: ")
    print(fieldnames)
	
	#fieldnames.append('Irn Number')
    #region CSV Setup
    #fileexists = os.path.isfile("./ConvertedInvoices/"+Path(filepath).stem+"/"+Path(filepath).stem+"_RequiredFiledsOnly.csv")
    #csv_file = open("./ConvertedInvoices/"+Path(filepath).stem+"/"+Path(filepath).stem+"_RequiredFiledsOnly.csv",mode='a')

    fileexists = os.path.isfile("./FinalOutputs/"+datetime+"_DATA.csv")
    csv_file = open("./FinalOutputs/"+datetime+"_DATA.csv",mode='a')
    
    writer = csv.DictWriter(csv_file,fieldnames)
    if not fileexists:
        writer.writeheader()
    #region end CSV SETUP
    writedict["PDF Name"] = str(Path(filepath).stem)+".PDF"

    for freg in data['invoices']:
        if re.compile(freg['name']).search(Path(filepath).stem):
            for i in freg['field']:
                name = i['datafieldname']
                pos = i['position']
                z = int(i["NoofSkips"])
                fout = i["FinalOutputField"]
                if pos != "NA":
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
                            if 'removefirstchar' in i and i['removefirstchar'] == '1':
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])[1:]
                            else:
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])
                        else:
                            print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data  
                            #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                            if 'removefirstchar' in i and i['removefirstchar'] == '1':
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])[1:]
                            else:
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
                            if 'removefirstchar' in i and i['removefirstchar'] == '1':
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])[1:]
                            else:
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])

                        else:
                            print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data  
                            #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                            if 'removefirstchar' in i and i['removefirstchar'] == '1':
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])[1:]
                            else:
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])

                    elif pos == "d":
                        dfpos[0] = dfpos[0]+1
                        print(name +" Data: "+df.iat[dfpos[0],dfpos[1]])#Final Data
                        writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                        if 'removefirstchar' in i and i['removefirstchar'] == '1':
                            writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])[1:]
                        else:
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
                            if 'removefirstchar' in i and i['removefirstchar'] == '1':
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])[1:]
                            else:
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])

                        else:
                            print(name +" Data: "+str(df.iat[dfpos[0],dfpos[1]+1]))#Final Data  
                            #writer.writerow({'fields':name,'data':str(df.iat[dfpos[0],dfpos[1]+1])})
                            if 'removefirstchar' in i and i['removefirstchar'] == '1':
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])[1:]
                            else:
                                writedict[fout] = str(df.iat[dfpos[0],dfpos[1]+1])

                    else :
                        print("Position not specified")
                else:
                    writedict[fout] = "0"
                #writer.writerow({'fields':'QRCode','data':barcode_data})
            
            #writedict['Irn Number'] = barcodedata
            
            writedict.update(barcodedata)


    print(writedict)
    if not not writedict  :
        print("Commiting to DB")
        DI.commitToDB(writedict)
        writer.writerow(writedict)
    else:
        print("Error no template for file in requiredFields.json")
    csv_file.close()


