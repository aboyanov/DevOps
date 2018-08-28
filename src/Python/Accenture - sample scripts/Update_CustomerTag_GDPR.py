#!/usr/bin/env python
import boto3
import json
import operator
import os
import csv
import sys


#Boto connection set
client = boto3.client(
	"ec2",
	#"eu-central-1", # for dh2
	"eu-west-1",     # for dh5
	aws_access_key_id="your_key_here",
	aws_secret_access_key="your_id_here",
)

#Get the file passed as argument
pathName = os.getcwd()
fileName = sys.argv[1]

#Open/Read the csv file
file = open(os.path.join(pathName, fileName), "rU")
reader = csv.reader(file, delimiter = ';')
next(reader, None) # skip the headers

#Itterate over a SCV file and get instance_id and customer_tag
instances = {}
for row in reader:
	instances[row[0]] = row[5]
	print(row[0] + " => " + row[5])
	
#Iterate over all instaces(in the file) and change/add Customer tag
for instance_id, customer_tag  in instances.items():
	response = client.create_tags(
		Resources=[
			instance_id,
		],
		Tags=[
			{
				'Key': 'Customer',     #Tag name
				'Value': customer_tag, #Tag value
			},
		],
	)