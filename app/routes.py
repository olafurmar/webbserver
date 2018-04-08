from app import app
from app.scriptModule import call_script, get_product_number
from flask import render_template, redirect, url_for, request, session, send_file, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app.fileHandler import saveFile, createZipFile, isFileCSV, isFileZIP
import os

products = ['PS-TK70C-10P0-M3', 'PS-TK70C-10P0-M3', 'DA-TK55P-20P1-M3']

@app.route('/', methods = ['GET', 'POST'])
@app.route('/uploadCSV', methods = ['GET', 'POST'])
def uploadCSV():
    if request.method == 'POST':
        csvfile = request.files['file']
        if  isFileCSV(csvfile):
            csvfilename = saveFile(csvfile)
            """products, error = get_product_number(csvfilename)"""
            """ spara bara filename om error är tomt 
            return render_template('uploadCSV.html', scriptMessage=error)"""
            session['csvfile'] = csvfilename
            session['productsNbr'] = products
            return render_template("uploadZIP.html", productNbr=products)
        return render_template('uploadCSV.html', fileMessage="Invalid file")
    return render_template('uploadCSV.html')

@app.route('/uploadZIP', methods = ['GET', 'POST'])
def uploadZIP():
    if request.method == 'POST':
        zipfile= request.files['file']
        selectedNbr = request.form.get('selectedNbr')
        if  isFileZIP(zipfile):
            zipfilename = saveFile(zipfile)
            csvfilename = session.get('csvfile', None)
            print("csvfilename: " + csvfilename)
            error = call_script(csvfilename, zipfilename, selectedNbr)
            if error:
                return render_template('uploadZIP.html', productNbr=session.get('productsNbr', None), scriptMessage="error in running script")
            returnPath = createZipFile(zipfilename)
            return send_file(returnPath, as_attachment=True)
        return render_template('uploadZIP.html', fileMessage="Invalid file", productNbr=session.get('productsNbr' , None))   
    return redirect(url_for('uploadCSV'))