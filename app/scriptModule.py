import subprocess
from subprocess import call
import sys
import os

path = "./Script/arena/psr2arena/"
def call_script(csv, zip, product):
    outputFilename = zip.split('.', 1)[0]
    scriptPath = path + "aip.py"
    csvPath = " -a " + "./Script/input/" + csv
    productPath = " -p " + product
    outputPath = " -o ./Script/output/" + outputFilename
    zipPath = " ./Script/input/" + zip
    start_script = "python2 " + scriptPath + csvPath + outputPath + productPath + " -k" + zipPath
    script_process = subprocess.Popen(start_script.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = script_process.communicate()
    return error.decode("utf-8")

def get_product_number(args):
    os.chdir("./Script/arena/psr2arena")
    hej = "python2 -c 'import aip; print aip.get_active_products(""./test_resources/arena_171002.csv"")'"
    start_script = "python2 -c 'import ./Script/arena/psr2arena/aip; print aip.get_active_products(/test_resources/arena_171002.csv)'"
    script_process = subprocess.Popen(hej.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = script_process.communicate()
    print ("output " + output.decode("utf-8"))
    print ("error " + error.decode("utf-8"))
    sys.stdout.flush()
    return output, error
