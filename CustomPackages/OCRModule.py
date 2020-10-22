import pytesseract

import os
import shutil
from pathlib import Path
import numpy as np

import re

import csv
import json
import zxing

import fitz
import pdf2image
from PIL import Image
import time
from copy import deepcopy


import cv2

import pyzbar.pyzbar as pyzbar

from unidecode import unidecode

from CustomPackages import DatabaseInteraction as DI
#IMAGE GENERATION VARIABLES
DPI = 500
OUTPUT_FOLDER = None
FIRST_PAGE = None
LAST_PAGE = None
FORMAT = 'jpg'
THREAD_COUNT = 1
USERPWD = None
USE_CROPBOX = False
STRICT = False




FileSpecificlocation = "./ConvertedInvoices/"

def save_images(pil_images,destination):

    x = destination+'temp/images/'
    try:
        print("MakingDIR")
        os.mkdir(destination+'temp/images')
    except OSError as e:
        print("OCRTEMPLATE:::::"+str(e))
    #This method helps in converting the images in PIL Image file format to the required image format
    index = 1
    for image in pil_images:
        image.save(x+"page_" + str(index) + ".jpg")
        index += 1
    return index

def GenerateImagesfromPDF(filepath,destination):
    
    start_time = time.time()
    pil_images = pdf2image.convert_from_path(filepath, dpi=DPI, output_folder=OUTPUT_FOLDER, first_page=FIRST_PAGE, last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD, use_cropbox=USE_CROPBOX, strict=STRICT)
    
    print ("Time taken : " + str(time.time() - start_time))
    index = save_images(pil_images,destination)
    return index
    


def GenerateOCR(filepath):
    destinationpath = FileSpecificlocation+Path(filepath).stem+'/'
    print("......Generating OCR.....")
    index = GenerateImagesfromPDF(filepath,destinationpath)
    text = ""
    for x in range(1,index):
        text += "\n" + pytesseract.image_to_string(Image.open(destinationpath+'temp/images/page_'+str(x)+'.jpg'))
    with open(destinationpath+'temp/'+"pytesseractextract.txt","w+") as x:
        text = unidecode(text)
        x.write(text)
    return text

def GenerateOCRTemplate(file):
    destinationpath = './TemplateGenerator/Output/'
    try:
        os.mkdir(destinationpath+'temp')
    except OSError as e:
        print("TEMPLETEER LSSGS :"+str(e))
    print("......Generating OCR.....")
    index = GenerateImagesfromPDF(file,destinationpath)
    text = ""
    for x in range(1,index):
        text += "\n" + pytesseract.image_to_string(Image.open(destinationpath+'temp/images/page_'+str(x)+'.jpg'))
    with open(destinationpath+Path(file).stem+".txt","w+") as x:
        text = unidecode(text)
        x.write(text)
    try:
        shutil.rmtree(destinationpath+'temp')
    except OSError as e:
        print(e)

def ParseOCR(datetime,filepath,text,barcodedata = {},reqfieldsfile = "requiredFields.json"):
    print("....Parsing OCR.....")

    writedict = {}
    qrdatalist = []

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
            for fs in freg['field']:
                datanameregex = fs['datafieldnameRegex']
                finaloutputfield = fs['FinalOutputField']
                dataonlyregex = fs['dataonlyRegex']
                forregexfull = datanameregex+dataonlyregex
                
                
                match = re.search(forregexfull,text,re.MULTILINE)
                if match:
                    print(match.group(0))
                
                    actualdata = re.search(dataonlyregex,match.group(0))  
                    if  'removefirstchar' in fs:
                        if fs['removefirstchar'] == '1':
                            print("ACTUAL DATA :::: ")
                            x = actualdata.group(0)
                            print(x)
                            tempdata = deepcopy(x)
                            print(tempdata)
                            tempdata = list(tempdata)
                            tempdata.remove(tempdata[0])
                            actualdata = "".join(tempdata)

                    if 'removefirstchar' not in fs:    
                        if actualdata:
                            print(actualdata.group(0)) 
                            print("Extracted INFO ::::: "+match.group(0)+":::::: Data :::::: "+actualdata.group(0))
                            writedict[finaloutputfield] = actualdata.group(0)
                        else:
                            actualdata = "Not Found"
                    else:
                        writedict[finaloutputfield] = actualdata
                        
                else:
                    writedict[finaloutputfield] = dataonlyregex

    #writedict['Irn Number'] = barcodedata
    writedict.update(barcodedata)
    if not not writedict:
        DI.commitToDB(writedict)
        writer.writerow(writedict)
    else:
        print("Error no template for file in requiredFields.json")
    csv_file.close()




def ParseOCR_QRcode(file):
    temploc = FileSpecificlocation+Path(file).stem+"/temp/images/"
    print(".....Parsing OCR QR data......")
    barcode_data = ""
    barcodeexists = False
    try:
        os.mkdir(temploc)
    except OSError as e:
        print(e)
    try:
        os.mkdir(temploc+'qrimages')
    except OSError as e:
        print(e)

    start_time = time.time()
    pil_images = pdf2image.convert_from_path(file, dpi=DPI, output_folder=OUTPUT_FOLDER, first_page=FIRST_PAGE, last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD, use_cropbox=USE_CROPBOX, strict=STRICT)
    print ("Time taken : " + str(time.time() - start_time))

    index = 1
    for image in pil_images:
        image.save(temploc+"qrimages/page_" + str(index) + ".jpg")
        index += 1
    for filename in os.listdir(temploc+"qrimages/"):
        image1 = cv2.imread(os.path.join(temploc+"qrimages/",filename))
        decodedobjects = pyzbar.decode(image1)
        if decodedobjects:
            print("YES")
            barcode_data = decodedobjects[0].data
            barcodeexists = True
            print(":::::::::::::::::::::::::::BARECODE DATA :::::::::::::::::::::::::::")
            print(barcode_data)
            print(":::::::::::::::::::::::::::BARECODE DATA END:::::::::::::::::::::::::::")
	
	#for i in range(1,index):
    #    reader = zxing.BarCodeReader()
    #    if os.path.isfile(temploc+"qrimages/page_" + str(index) + ".jpg"):
    #        image1 = cv2.imread(emploc+"qrimages/page_" + str(index) + ".jpg")
            
                
            #barcode = reader.decode(temploc+"qrimages/page_" + str(index) + ".jpg")
            #if barcode:
            #    barcodeexists = True
            #    barcode_data = barcode.raw
    
    if barcodeexists:
        return barcode_data
    else:
        return ""
