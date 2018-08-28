import boto3
import json
import operator
import os
import csv
import sys
from openpyxl import load_workbook

#############################################################

###### TO DO : 
# This script is designed to take a SCV or EXCEL file		#
# itterate over it and update/create provided as args tags. #
# ./add_tag.py file_path instance_name tag_name

# file_path = String
#	- The path to the file
#  instance_name = String
#	- 
# tag_name = String
#	- The name of the column in the Excel with the values
#   - The name will also be used as a name for the tag

#############################################################


###Set the boto3 connection
client = boto3.client(
	"ec2",
	#"eu-central-1",   # for dh2
	"eu-west-1",     # for dh5
	aws_access_key_id = "your_key_here",
	aws_secret_access_key = "your_key_here",
)

###Get the file passed as argument
#pathName = os.getcwd()
#fileName = sys.argv[1]
#
####Open/Read the csv/xlsx file
#file = open(os.path.join(pathName, fileName), "rU")
#reader  = ''
#is_excel_flag = False
#
#if ".xls" in file.name:
#	reader = load_workbook(filename = file.name)
#	reader = reader.active
#	is_excel_flag = True
#else:
#	reader = csv.reader(file, delimiter = ';')
#	next(reader, None) # skip the headers
#
####Itterate over a SCV/EXCEL file and get instance_id and GDPR_value
#
#count = 0
#instances = {}
#for row in reader:
#	
#	if is_excel_flag == True:
#		if row[0].value:
#			#count = count + 1
#			#print(row[0].value)
#			customer_tag = row[1].value or ''
#			instances[row[0].value] = customer_tag
#			#print(str(row[0].value) + " => " + customer_tag)
#	else:
#		instances[row[0]] = row[20]
#		
#print(count)
###Get all instances from the region

instances = client.describe_instances()['Reservations']
instances_ids = {}

###Iterate over each instance and extract InstanceID + ClusterId
for instance in instances:
	inst_entry = instance["Instances"]
	for property in inst_entry:
		instance_id = property["InstanceId"]
		instances_ids[instance_id] = "k"
	
###Iterate over all instaces(in the file) and change/add GDPR value(Yes/No)

counter = 0

#print(instances)

for instance_id, GDPR_value in instances_ids.items():
	#if counter > 0:
	print(instance_id + " => " + GDPR_value)
	try:
		response = client.create_tags(
			Resources=[
				instance_id,
				#"i-00e7756f2d828d330" # if you want a certain instance/s
			],
			Tags=[
				{
					'Key': 'GDPR',      #Tag name
					#'Key': 'Customer',
					#'Value': GDPR_value, #Tag value
					'Value': 'Yes'
				},
			],
		)
	except Exception as e:
		print('\nException:{exception}\n'.format(exception = e))
		continue
	print(response)
	#counter = counter + 1