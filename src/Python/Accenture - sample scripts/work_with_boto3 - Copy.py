import boto3
import json
import operator
import os

#Connection set
client = boto3.client(
	"ec2",
	#"eu-central-1",
	"eu-west-1",     # for dh5
	aws_access_key_id = "your_id",
	aws_secret_access_key = "your_id",
)

instances = client.describe_instances()['Reservations']
instances_ids = {}


#Iterate over each instance and extract InstanceID + ClusterId
for instance in instances:
	inst_entry = instance["Instances"]
	for property in inst_entry:
		instance_id = property["InstanceId"]
		instances_ids[instance_id] = "k"

		
print("Total number of customers {}".format(len(instances_ids.keys()))) 

#Write the sorted histogram as json file in current dir.
with open("result.json", "w") as fp:
	json.dump(instances_ids, fp,sort_keys = True, indent = 4,  ensure_ascii=False)
	
print("The file result was stored in " + os.getcwd())