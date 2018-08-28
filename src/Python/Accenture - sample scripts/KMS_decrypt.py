#!/usr/bin/python

import subprocess
import os
from subprocess import Popen
import datetime
import boto3
import sys

#### Decrypt the ecrypted data(username & password) and pass it to the RPA
def decrypt():
    try:
        file = sys.argv[1]
    except IndexError:
        print "Provide a filename with encrypted details as argument.."
    with open(file,'rb') as f:
        data = f.read()
    kms = boto3.client('kms',region_name='eu-central-1')
    #### Split encrypted data from passphrase
    dec_data = data.split('###')[0]
    context = data.split('###')[1]
    response = kms.decrypt(CiphertextBlob=dec_data, EncryptionContext={'string': context})
    #### Split username from password
    username = response['Plaintext'].split("/")[0]
    password = response['Plaintext'].split("/")[1]
    print "Username: %s , Password: %s" % (username, password)
    return username, password
	
#### Get username and password
user, passw = decrypt()

#### Run the batch file which will execute the RPA script
command = "runRemedyForce.bat " + user + " " + passw
p = Popen(command, cwd=r"C:\Users\Administrator\Documents\UiPath\Outlook-Email", shell=True)
stdout, stderr = p.communicate()

