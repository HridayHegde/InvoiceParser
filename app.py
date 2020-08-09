import os

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

from pathlib import Path

import json
from CustomPackages import InvoiceDataExtractor as InDe
from TemplateGenerator import TemplateGen as TG
import shutil

# Initialize the Flask application
app = Flask(__name__)

MYDIR = os.path.dirname(__file__)
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'PDFInvoices/'
app.config['OUTPUT_FOLDER'] = 'FinalOutputs/'
app.config['ZIP_FOLDER'] = 'ZipOutput/'
app.config['MAIN_FOLDER'] =''
app.config['TEMPLATE_FOLDER']='TemplateGenerator/Uploads/'
app.config['TEMPLATE_OUTPUT']='TemplateGenerator/Output/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['pdf','PDF'])


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    try:
        os.mkdir("PDFInvoices")
    except OSError as e:
        print(e)
    try:
        os.mkdir("FinalOutputs")
    except OSError as e:
        print(e)
    try:
        os.mkdir("ConvertedInvoices")
    except OSError as e:
        print(e)
    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded files
    uploaded_files = request.files.getlist("file[]")
    
    filenames = []
    for file in uploaded_files:
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            print(file)
            # Make the filename safe, remove unsupported chars
            filename, file_extension = os.path.splitext(file.filename)
            filename = secure_filename(Path(filename).stem)
            z = filename
            filename = filename+file_extension

            
            # Move the file form the temporal folder to the upload
            # folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Save the filename into a list, we'll use it later
            
            x = z+"_RequiredFiledsOnly.csv"
            #filenames.append(filename)
            #filenames.append(x)
            
            # Redirect the user to the uploaded_file route, which
            # will basicaly show on the browser the uploaded file
    # Load an html page with a link to each uploaded file
    filenames.append("output_zip.zip")
    InDe.main()
    head = "Zipped Output"
    return render_template('upload_main.html', filenames=filenames,heading=head)

@app.route('/uploadjson', methods=['POST'])
def uploadmain():
    # Get the name of the uploaded files
    
    uploaded_files = request.files.getlist("file[]")
    try:
        os.remove("requiredFields.json")
    except:
        print("File Doesnt Exist")

    uploaded_files[0].save("./requiredFields.json")
    
    return render_template('index.html',scroll='json')

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploadtemp/<filename>')
def uploaded_template(filename):
    
    return send_from_directory(app.config['TEMPLATE_OUTPUT'],filename,mimetype='application/octet-stream')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['ZIP_FOLDER'],filename)

@app.route('/download')
def download_file():
    filename = "requiredFields.json"

    return send_from_directory(app.config['MAIN_FOLDER'],filename,as_attachment=True,)


@app.route('/templategen', methods=['POST'])
def templategen():
    TG.empty()
    filenames = []
    method = request.values.get("method") 
    x1 = request.values.get("x")
    uploaded_files = request.files.getlist("file[]")
    if method == "OCR":
        for filex in uploaded_files:
            
            if filex and allowed_file(filex.filename):
                print("FILENAMEFOR TEMPLATE ::::: "+str(filex))
                filename, file_extension = os.path.splitext(filex.filename)
                filename = secure_filename(Path(filename).stem)
                filename1 = filename+".txt"
                filename = filename+file_extension
                filenames.append(filename1)
                filex.save(os.path.join(app.config['TEMPLATE_FOLDER'], filename))
        TG.generate("OCR")
    elif method == "TAB":
        for filex in uploaded_files:
            if filex and allowed_file(filex.filename):
                print("FILENAMEFOR TEMPLATE ::::: "+str(filex))
                filename, file_extension = os.path.splitext(filex.filename)
                filename = secure_filename(Path(filename).stem)
                filename1 = filename+".csv"
                filename = filename+file_extension
                filenames.append(filename1)
                filex.save(os.path.join(app.config['TEMPLATE_FOLDER'], filename))
        TG.generate("TAB")

    head = "Templates"
    return render_template('upload_template.html', filenames=filenames,heading=head)




if __name__ == '__main__':
    app.run(
        #host="127.0.0.1",
        #port=int("80"),
        #debug=True
        threaded=True,
        port=5000,
        debug=False
    )