import boto3

REGION = "eu-central-1"

#Connection set
client = boto3.client(
	"ec2",
	REGION,
	aws_access_key_id="",
	aws_secret_access_key="",
)

instances = client.describe_instances()['Reservations']
private_dnses = []

#Iterate over each instance and get the private dns
for instance in instances:
	inst_entry = instance["Instances"]
	for property in inst_entry:
		
		#Just in case
		try:
			private_dnses.append(property['PrivateDnsName'])
		except Exception:
			pass

#Create ansible host file
with open("hosts.info", "w") as f:
	f.write("[{0}]\n".format(REGION))
	
	for each_private_dns in private_dnses:
		f.write(each_private_dns + "\n")
