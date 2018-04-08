from app import app
import unittest
import os
from werkzeug.utils import secure_filename
import flask
from io import BytesIO
class testClass(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        app.testing = True
        app = app.test_client()

    def testCSVupload(self):
        filename = './Script/Test_data/success.csv'
        filenameToBechecked = 'Script_Test_data_success.csv'
        products = ['PS-TK70C-10P0-M3', 'PS-TK70C-10P0-M3', 'DA-TK55P-20P1-M3']
        csvfile = open(filename, "r+")
        csvfile.read()
        with app.test_client() as c:
            result = c.post('/uploadCSV', data=dict(file=csvfile))
            self.assertEqual(result.status_code, 200)
            self.assertEqual(flask.session['csvfile'], filenameToBechecked)
            self.assertEqual(flask.session['productsNbr'], products)
                
    
    def testZIPupload(self):
        csvfilename = "Script/Test_data/success.csv"
        zipfile = open("Script/Test_data/success.zip", "r+")
        zipfile.read()
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['csvfile'] = csvfilename
                sess['productsNbr'] = ['PS-TK70C-10P0-M3', 'PS-TK70C-10P0-M3', 'DA-TK55P-20P1-M3']
            result = c.post('/uploadZIP', data=dict(file=zipfile, selectedNbr='PS-TK70C-10P0-M3'))
            self.assertEqual(result.status_code, 200) 

        

if __name__ == '__main__':
    unittest.main()