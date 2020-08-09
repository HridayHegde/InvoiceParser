from CustomPackages import TabulaModule
from CustomPackages import OCRModule

import os
import shutil

originfolder = "./TemplateGenerator/Uploads"


def empty():
    try:
        shutil.rmtree("./TemplateGenerator/Uploads")
    except OSError as e:
        print(e)

    try:
        shutil.rmtree("./TemplateGenerator/Output")
    except OSError as e:
        print(e)

    try:
        os.mkdir("./TemplateGenerator/Uploads")
    except OSError as e:
        print(e)

    try:
        os.mkdir("./TemplateGenerator/Output")
    except OSError as e:
        print(e)

def generate(method):
    file_set = []
    for file in os.listdir(originfolder):
        if file.endswith(".pdf") or file.endswith(".PDF"):
            file_set.append(os.path.join(originfolder, file))


    if method == "OCR":
        print("---------------OCR TEMPLATING---------------")
        for f in file_set:
            OCRModule.GenerateOCRTemplate(f)
            
    
    elif method == "TAB":
        print("---------------TABULA TEMPLATING---------------")
        for f in file_set:
            TabulaModule.GenerateCSVTemplate(f)
