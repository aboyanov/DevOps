import os
import csv
import sys

#Instances[scv[0]] = scv[5]

pathName = os.getcwd()
fileName = sys.argv[1]

file = open(os.path.join(pathName, fileName), "rU")
reader = csv.reader(file, delimiter=';')
next(reader, None)  # skip the headers

ins = {}
for row in reader:
	ins[row[0]] = row[5]
	#for column in row:
	#	print(column)
	
for instance_id, customer_tag  in ins.items():
	print(instance_id + " => " + customer_tag)