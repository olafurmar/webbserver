from app import app
from werkzeug.utils import secure_filename
import os
import shutil

def saveFile(file):
    if not app.testing:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("whyyyyy")
        return filename
    print("testing")

def createZipFile(filename):
    outputFilename = filename.split('.', 1)[0]
    outputPath = os.path.join(os.getcwd(), 'Script/output/' + outputFilename)
    zipPath = os.path.join(os.getcwd(), 'Script/zip/' + outputFilename)
    shutil.make_archive(zipPath, 'zip', outputPath)
    return zipPath + '.zip'

def isFileZIP(file):
    zipSet = set(['zip'])
    filename = file.filename
    return file and '.' in filename and filename.rsplit('.', 1)[1] in zipSet

def isFileCSV(file):
    csvSet = set(['csv'])
    filename = file.filename
    return file and '.' in filename and filename.rsplit('.', 1)[1] in csvSet