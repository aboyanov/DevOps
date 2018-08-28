import boto3
import json
import operator
import os

#Connection set
client = boto3.client(
	"ec2",
	"eu-central-1",
	aws_access_key_id = "your_id",
	aws_secret_access_key = "your_key",
)

instances = client.describe_instances()['Reservations']
instances_histogram = {}


#Iterate over each instance and extract InstanceID + ClusterId
for instance in instances:
	inst_entry = instance["Instances"]
	for property in inst_entry:
		instance_id = property["InstanceId"]
		 
		all_tags = property["Tags"]
		
		for tag_pair in all_tags:
			
			for pair in tag_pair:
				if tag_pair["Key"] == "ClusterId" and len(tag_pair["Key"]) > 0:
					cust_name = tag_pair["Value"]
	
	# Put the extracted metadata inside the histogram
	if cust_name in instances_histogram:
		instances_histogram[cust_name].append(instance_id)
	else:
		instances_histogram[cust_name] = [instance_id]

#Sort the instances histogram by key		
instances_histogram = dict(sorted(instances_histogram.items(), key = operator.itemgetter(0)))

 
print("Total number of customers {}".format(len(instances_histogram.keys()))) 

#Write the sorted histogram as json file in current dir.
with open("result.json", "w") as fp:
	json.dump(instances_histogram, fp,sort_keys = True, indent = 4,  ensure_ascii=False)
	
print("The file result was stored in " + os.getcwd())