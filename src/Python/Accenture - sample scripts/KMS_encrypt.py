#!/usr/bin/python
#Creator: AAAM L3 EU team
#Part of: a KMS solution for credenetials management in the Windows Jumpbox

import boto3
import socket
import sys

key = 'key_here'
kms = boto3.client('kms',region_name='eu-central-1')
plain = sys.argv[1]
cipher = sys.argv[2]

response = kms.encrypt(KeyId=key, Plaintext=plain,EncryptionContext={'string': cipher})

encrypted = response['CiphertextBlob']
text = encrypted + '###' + cipher

IP = '10.0.40.150'
PORT = '43000'

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP,int(PORT)))
    sock.send(text)
except socket.error as e:
    print e
finally:
    sock.close()
