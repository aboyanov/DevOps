import boto3
import csv

awsdc = [
	"us-east-1",
	"us-east-2",
	"us-west-1",
	"us-west-2",
	"ap-south-1",
	"ap-northeast-2",
	"ap-southeast-1",
	"ap-southeast-2",
	"ap-northeast-1",
	"ca-central-1",
	"eu-central-1",
	"eu-west-1",
	"eu-west-2",
	"eu-west-3",
	"sa-east-1"
]


def listInstances( region ):
	csvname = 'instances_with_tags_' + region + '.csv'		
		
	# Set connection
	client = boto3.client(
		"ec2",
		region,
		aws_access_key_id = "your_id_here",
		aws_secret_access_key = "your_key_here",
	)

	# Get list of instances
	reservations = client.describe_instances()['Reservations']


	# Get list of tags across all instances (needed in case some isntance have not the same number of tags)
	taglist = {}
	for reservation in reservations:
		instances = reservation["Instances"]
		for instance in instances:
			if "Tags" in instance.keys():
				for tag in instance["Tags"]:
					taglist[tag["Key"]] = 1

	csvheader = ["InstanceId", "AvailabilityZone", "PrivateDnsName", "PrivateIpAddress", "PublicDnsName", "PublicIpAddress", "State"]

	for tag in sorted(taglist):
		csvheader = csvheader + [tag]

	# Write CSV file
	with open(csvname, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow( csvheader )
		print ("result saved to instances_aws.csv")
		for reservation in reservations:
			instances = reservation["Instances"]
			for instance in instances:
				row = [ instance.get("InstanceId", "").encode("utf-8"),
					instance["Placement"]["AvailabilityZone"].encode("utf-8"),
					instance.get("PrivateDnsName","").encode("utf-8"),
					instance.get("PrivateIpAddress","").encode("utf-8"),
					instance.get("PublicDnsName","").encode("utf-8"),
					instance.get("PublicIpAddress","").encode("utf-8"),
					instance["State"]["Name"].encode("utf-8"),
					]
				instancetags = {}
				for tag in instance["Tags"]:
					instancetags[tag["Key"]] = tag["Value"].encode("utf-8")
				for tag in sorted(taglist):
					row += [ instancetags.get(tag, "") ]
				csvwriter.writerow( row )


for region in awsdc:
	listInstances( region )
