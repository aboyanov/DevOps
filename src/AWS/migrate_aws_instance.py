#!/usr/bin/env python
import pymongo
import json
import sys
import os
from os import path
from bson.objectid import ObjectId
import boto3
import time
from os import path
from pymongo import MongoClient
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from util_modules import information_lookup
from util_modules import util
from util_modules import get_order_information



logger = get_order_information.logger


# Place a order in nodejs DB in order table with new new region and old orderit append "temp" at the end.
# Put the order in order queue and ask controller to luanch a new instance
def place_new_instace_order(nodejs_db, old_base_order_id, new_region, environment):
    result = nodejs_db.orders.find({"OrderItems.OrderItemUId":old_base_order_id}) 
    for base_order in result:
        
        new_order_item_uid = base_order['OrderUId'] + 'temp'
        base_order['OrderItems'][0]['OrderItemUId'] = new_order_item_uid
        base_order['OrderItems'][0]['Status'] = "Placed"
        base_order['_id'] = ObjectId()
        access_url = base_order["OrderItems"][0]["AccessLinkURL"] 
        hostnamne = information_lookup.url_lookup(new_region, environment)
        url_parts = access_url.split('/')
        url_parts[2] = hostnamne
        new_access_url = "/".join(url_parts) 
        base_order["OrderItems"][0]["AccessLinkURL"] = new_access_url
        for config in base_order['OrderItems'][0]['Config']:
            if config['Key'] == 'DeploymentRegion':
                config['Value'] = new_region

        orderqueues_order = { "_id" : ObjectId(), "OrderUId" : new_order_item_uid, "Status" : "Received", "__v" : 0 }
        nodejs_db.orders.insert(base_order)
        nodejs_db.orderqueues.insert(orderqueues_order)
    return new_order_item_uid, new_access_url

def create_snapshots_from_old_instance(old_instance_id, aws_region_code, old_base_order_id):
    finished_code = ["sda1","sdb","sdc"]
    while len(finished_code) != 0:
        if "sda1" in finished_code:
            sda1_snapshot_id = create_snapshot(old_instance_id, aws_region_code, old_base_order_id, "sda1")
        if "sdb" in finished_code:
            sdb_snapshot_id = create_snapshot(old_instance_id, aws_region_code, old_base_order_id, "sdb")
        if "sdc" in finished_code:
            sdc_snapshot_id = create_snapshot(old_instance_id, aws_region_code, old_base_order_id, "sdc")
        finished_code = wait_snapshots_finished([sda1_snapshot_id, sdb_snapshot_id, sdc_snapshot_id], aws_region_code, finished_code)
    
    return sda1_snapshot_id, sdb_snapshot_id, sdc_snapshot_id


def create_snapshot(old_instance_id, aws_region_code, old_base_order_id, device_name):
    client = boto3.client('ec2', aws_region_code)
    response = client.stop_instances(
        InstanceIds=[
            old_instance_id,
        ]
    )

    while True:
        response = client.describe_instances(
            InstanceIds=[
                old_instance_id,
            ],
        )
        if response['Reservations'][0]['Instances'][0]['State']['Name'] != 'stopped':
            logger.info("Wating...... instance is stopping")
            time.sleep(30)
        else:
            break

    # logger.info("instance stopped")

    for volume in response['Reservations'][0]['Instances'][0]['BlockDeviceMappings']:
        if volume['DeviceName'] == '/dev/' + device_name:
            sdb_volume_id = volume['Ebs']['VolumeId']
            response = client.create_snapshot(
                Description= device_name + ' snapshot for ' + old_instance_id,
                VolumeId=sdb_volume_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {
                                'Key': 'instanceOrderId',
                                'Value': old_base_order_id
                            },
                            {
                                'Key': 'deviceName',
                                'Value': device_name
                            },
                        ]
                    },
                ],
            )
            snapshot_id = response['SnapshotId']
    return snapshot_id



def copy_snapshots_to_new_region(snapshot_ids, aws_region_code, new_aws_region_code, old_instance_id, old_base_order_id):
    finished_code = ["sda1","sdb","sdc"]
    while len(finished_code) != 0:
        if "sda1" in finished_code:
            new_sda1_snapshot_id = copy_snapshot_to_new_region(snapshot_ids[0], aws_region_code, new_aws_region_code, 'sda1 snapshot for ' + old_instance_id, old_base_order_id, "sda1")
        if "sdb" in finished_code:
            new_sdb_snapshot_id = copy_snapshot_to_new_region(snapshot_ids[1], aws_region_code, new_aws_region_code, 'sdb snapshot for ' + old_instance_id, old_base_order_id, "sdb")
        if "sdc" in finished_code:
            new_sdc_snapshot_id = copy_snapshot_to_new_region(snapshot_ids[2], aws_region_code, new_aws_region_code, 'sdc snapshot for ' + old_instance_id, old_base_order_id, "sdc")
        finished_code = wait_snapshots_finished([new_sda1_snapshot_id, new_sdb_snapshot_id, new_sdc_snapshot_id], new_aws_region_code, finished_code)
    return new_sda1_snapshot_id, new_sdb_snapshot_id, new_sdc_snapshot_id
        



#Copy snapshot to new region
def copy_snapshot_to_new_region(snapshot_id, aws_region_code, new_aws_region_code, description, old_base_order_id, device_name):
    client = boto3.client('ec2',region_name=new_aws_region_code)
    response=client.copy_snapshot(SourceSnapshotId=snapshot_id,
            SourceRegion=aws_region_code,
            DestinationRegion=new_aws_region_code,
            Description=description,
            )
    new_snapshot_id = response['SnapshotId']
    response = client.create_tags(
        Resources=[
                new_snapshot_id,
            ],
        Tags=[
            {
                'Key': 'instanceOrderId',
                'Value': old_base_order_id
            },
            {
                'Key': 'deviceName',
                'Value': device_name
            },
        ]
    )
    # new_snapshot_id = response['SnapshotId']
    return new_snapshot_id
    
#Waiting snapshot finished so ensure create volume function working correctly
def wait_snapshots_finished(snapshot_ids, aws_region_code, finished_code):
    
    client = boto3.client('ec2',region_name=aws_region_code)
    completed_number = 0
    error_code = []
    while len(finished_code) != 0:
        response = client.describe_snapshots(
            SnapshotIds=snapshot_ids,
        )
        snapshots = response['Snapshots']
        for snapshot in snapshots:

            for tag in snapshot['Tags']:
                if tag["Key"] == "deviceName":
                    device_name = tag["Value"]
            if snapshot['State'] == 'completed':
                finished_code.remove(device_name)
                snapshot_ids.remove(snapshot['SnapshotId'])
            elif snapshot['State'] == 'error':
                finished_code.remove(device_name)
                error_code.append(device_name)
            else:
                logger.info("Creating snapshots..." + str(finished_code))
                time.sleep(30)
    return error_code

def create_volume_from_snapshot(new_snapshot_id ,new_aws_region_code, old_instance_id, new_region, domain_context_root):

    client = boto3.client('ec2',region_name=new_aws_region_code)
    availability_zone = information_lookup.availability_zone_lookup(new_region)
    response = client.create_volume(
        AvailabilityZone=availability_zone,
        SnapshotId=new_snapshot_id,
        VolumeType='gp2',
        TagSpecifications=[
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'note',
                        'Value': 'Volume for migrating instance ' + old_instance_id
                    },
                    {
                        'Key': 'ClusterId',
                        'Value': domain_context_root
                    },
                    {
                        'Key': 'Backup-Daily',
                        'Value':'true'
                    },
                    {
                        'Key':'Backup-Weekly',
                        'Value': 'true'

                    }

                ]
            },
        ]
    )
    return response['VolumeId']
    

def create_volumes_from_snapshots(new_snapshot_ids, new_aws_region_code, old_instance_id, new_region, domain_context_root):
    client = boto3.client('ec2',region_name=new_aws_region_code)
    availability_zone = information_lookup.availability_zone_lookup(new_region)
    volume_ids = []
    for new_snapshot_id in new_snapshot_ids:
        response = client.create_volume(
            AvailabilityZone=availability_zone,
            SnapshotId=new_snapshot_id,
            VolumeType='gp2',
            TagSpecifications=[
                {
                    'ResourceType': 'volume',
                    'Tags': [
                        {
                            'Key': 'note',
                            'Value': 'Volume for migrating instance ' + old_instance_id
                        },
                        {
                            'Key': 'ClusterId',
                            'Value': domain_context_root
                        },
                        {
                            'Key': 'Backup-Daily',
                            'Value':'true'
                        },
                        {
                            'Key':'Backup-Weekly',
                            'Value': 'true'

                        }

                    ]
                },
            ]
        )
        volume_ids.append(response['VolumeId'])
    return volume_ids



def wait_for_volume_completed_and_instnace_started(volume_ids, new_order_item_uid, new_aws_region_code):
    client = boto3.client('ec2', new_aws_region_code)
    filters = [{'Name': 'tag:orderId','Values': [new_order_item_uid] }]

    while True:
        response = client.describe_instances(Filters=filters)
        instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
        if instance_state == 'running':
            break
        else:
            logger.info("Starting instance...")
            time.sleep(30)
    while True:
        response = client.describe_volumes(
            VolumeIds=volume_ids,
        )
        if response['Volumes'][0]['State'] == 'available' and response['Volumes'][1]['State'] == 'available':
            break
        else:
            logger.info("Creating volumes...")

def detach_volume_from_new_instance(new_instance_id, new_aws_region_code):
    client = boto3.client('ec2', new_aws_region_code)


    response = client.stop_instances(
        InstanceIds=[
            new_instance_id,
        ]
    )

    while True:
        response = client.describe_instances(
            InstanceIds=[
                new_instance_id,
            ],
        )
        if response['Reservations'][0]['Instances'][0]['State']['Name'] != 'stopped':
            logger.info("Stopping instance...")
            time.sleep(30)
        else:
            break

    logger.info("instance stopped")

    time.sleep(60)
    for volume in response['Reservations'][0]['Instances'][0]['BlockDeviceMappings']:
        if volume['DeviceName'] == '/dev/sda1':
            sdb_volume_id = volume['Ebs']['VolumeId']
            response = client.detach_volume(
                InstanceId=new_instance_id,
                VolumeId=sdb_volume_id,
            )
        elif volume['DeviceName'] == '/dev/sdb':
            sdb_volume_id = volume['Ebs']['VolumeId']
            response = client.detach_volume(
                InstanceId=new_instance_id,
                VolumeId=sdb_volume_id,
            )
        elif volume['DeviceName'] == '/dev/sdc':
            sdc_volume_id = volume['Ebs']['VolumeId']
            response = client.detach_volume(
                InstanceId=new_instance_id,
                VolumeId=sdc_volume_id,
            )

def get_new_instance_details(new_order_item_uid,  new_aws_region_code):
    client = boto3.client('ec2', new_aws_region_code)
    filters = [{'Name': 'tag:orderId','Values': [new_order_item_uid] }]
    response = client.describe_instances(Filters=filters)
    new_instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
    new_instnace_private_dns = response['Reservations'][0]['Instances'][0]['PrivateDnsName']
    return new_instance_id, new_instnace_private_dns



def attach_new_volume(new_instance_id, new_aws_region_code, new_volume_id, device_name):
    client = boto3.client('ec2', new_aws_region_code)
    response = client.attach_volume(
        Device='/dev/' + device_name,
        InstanceId=new_instance_id,
        VolumeId=new_volume_id,
    )

def start_instance(new_instance_id, new_aws_region_code):
    client = boto3.client('ec2', new_aws_region_code)
    response = client.start_instances(
        InstanceIds=[
            new_instance_id,
        ]
    )



def configure_and_start_splunk(new_private_dns, new_access_url):
    # configure_atr_command 

    command = " ssh -o StrictHostKeyChecking=no " + new_private_dns + " &>/dev/null"
    command += " << EOF\n sudo su - centos\n cd /var/www/aaam-atr-uiv2/config"
    command += " \n sed -i -e 's/relay=https:.*/relay=" +  new_access_url.replace('/','\/') + "\/en-US\/saml\/acs/g' authentication.conf"
    command += " \n sed -i -e 's/idpSLOUrl = https:\/\/.*/idpSLOUrl = " +  new_access_url.replace('/','\/') + "\/logout/g' authentication.conf"
    command += " \nEOF"


    command = " ssh -o StrictHostKeyChecking=no " + new_private_dns + " &>/dev/null"
    command += " << EOF\n sudo su splunk\n cd /opt/splunk/etc/system/local"
    command += " \n sed -i -e 's/relay=https:.*/relay=" +  new_access_url.replace('/','\/') + "\/en-US\/saml\/acs/g' authentication.conf"
    command += " \n sed -i -e 's/idpSLOUrl = https:\/\/.*/idpSLOUrl = " +  new_access_url.replace('/','\/') + "\/logout/g' authentication.conf"
    command += " \n ~/bin/splunk restart >/dev/null\nEOF"
    os.system(command)


def copy_controller_mongo(old_region, new_region, environment, sap_contract_id, project_id, customer_enterprise_id):
    old_controller_name = old_region + environment
    new_controller_name = new_region + environment
    old_controller_ip =  information_lookup.get_controller_ip(old_controller_name)
    new_controller_ip =  information_lookup.get_controller_ip(new_controller_name)
    old_client = MongoClient(old_controller_ip,27017)
    new_client = MongoClient(new_controller_ip,27017)
    old_controller_db = old_client['aiamhpdpintegration']
    new_controller_db = new_client['aiamhpdpintegration']

    
    new_result_order = new_controller_db.orderRequest.find({"$and":[{"config":{ "$elemMatch": {"Value" : sap_contract_id, "Key" : "SAPContractID"}}},{"config":{ "$elemMatch": {"Key":"CustomerEnterpriseID","Value":customer_enterprise_id}}},{"projectId":project_id},{"responseStatus" : "OK"}]})
    for new_value_order in new_result_order:
        if new_value_order['productId'] == "9c4f3e6a-c2ea-e511-8053-180373e9b33d":
            new_server = new_value_order['server']
            if new_server == "":
                logger.warn("The order is not fulfilled")
                continue
            new_result_server = new_controller_db.server.find({"_id":ObjectId(new_server)})
            for value_server in new_result_server:
                new_value_server = value_server
                
    old_result_order = old_controller_db.orderRequest.find({"$and":[{"config":{ "$elemMatch": {"Value" : sap_contract_id, "Key" : "SAPContractID"}}},{"config":{ "$elemMatch": {"Key":"CustomerEnterpriseID","Value":customer_enterprise_id}}},{"projectId":project_id},{"responseStatus" : "OK"}]})
    for old_value_order in old_result_order:
        if old_value_order['productId'] == "9c4f3e6a-c2ea-e511-8053-180373e9b33d":
            old_server = old_value_order['server']
            if old_server == "":
                logger.warn("The order is not fulfilled")
                continue
            old_result_server = old_controller_db.server.find({"_id":ObjectId(old_server)})
            old_result_ordererRequest = old_controller_db.orderRequest.find({"server":old_server})
            old_result_ticketAnalysis = old_controller_db.ticketAnalysis.find({"server":old_server})
            old_result_employeeActivityReport = old_controller_db.employeeActivityReport.find({"server":old_server})
            old_result_projectDemography = old_controller_db.projectDemography.find({"serverId":old_server})			
            
            for old_value_server in old_result_server:
                logger.info("copy Server entry in controller : " + old_server)
                new_value_server["_id"] = ObjectId(old_server)
                new_value_server["installedProducts"] = old_value_server["installedProducts"]
                new_controller_db.orderRequest.find({"$and":[{"config":{ "$elemMatch": {"Value" : sap_contract_id, "Key" : "SAPContractID"}}},{"config":{ "$elemMatch": {"Key":"CustomerEnterpriseID","Value":customer_enterprise_id}}},{"projectId":project_id},{"responseStatus" : "OK"}]})
                new_controller_db.server.insert(new_value_server) 
                response = new_controller_db.orderRequest.update({"$and":[{"config":{ "$elemMatch": {"Value" : sap_contract_id, "Key" : "SAPContractID"}}},{"config":{ "$elemMatch": {"Key":"CustomerEnterpriseID","Value":customer_enterprise_id}}},{"projectId":project_id},{"responseStatus" : "OK"}]},{"$set":{"server":old_server}})
        

            for old_value_order in old_result_ordererRequest:
                if old_value_order['productId'] != "55cdb588-c8d5-4f4d-8f9c-0905ee090df9" and old_value_order['productId'] != "9c4f3e6a-c2ea-e511-8053-180373e9b33d" and old_value_order['productId'] != "5b384be8-62bf-419f-bb10-2ff5287afd71":
                    new_controller_db.orderRequest.insert(old_value_order)
            logger.info("Copying Order entries in controller")

            for old_value_ta in old_result_ticketAnalysis:
                new_controller_db.ticketAnalysis.insert(old_value_ta)
            logger.info("Copying TickerAnalysis entries in controller")

            for old_value_emp in old_result_employeeActivityReport:
                new_controller_db.employeeActivityReport.insert(old_value_emp)
            logger.info("Copying employeeActivityReport entries in controller")
            
            for old_value_proj in old_result_projectDemography:
                new_controller_db.projectDemography.insert(old_value_proj)
            logger.info("Copying projectDemography entries in controller")

def configure_apps(all_app_orders, new_private_dns, new_access_url, old_access_url, old_controller_name, new_controller_name):
    for order in all_app_orders:
        product_type = information_lookup.get_product_type(order["OrderItems"][0]["ProductUId"])
        if product_type == "AAAM ATR App":
            configure_atr(new_private_dns, new_access_url, old_access_url, old_controller_name, new_controller_name)        

def configure_atr(new_private_dns, new_access_url, old_access_url, old_controller_name, new_controller_name):
    # configure_atr_command 
    
    new_domain_name =  new_access_url.split("/")[2]
    old_domain_name = old_access_url.split("/")[2]
    new_domain_root_context = new_access_url.split("/")[3]
    old_domain_root_context = old_access_url.split("/")[3]
    logger.info("Configuration ART app")
    logger.info("new Rundeck URL: " + new_domain_name + "/rundeck-" + new_domain_root_context)
    logger.info("new ATR URL: " + new_domain_name + "/atr-" + new_domain_root_context)
    new_domain_root_context = new_access_url.split("/")[3]
    old_domain_root_context = old_access_url.split("/")[3]
    old_controller_public_dns = information_lookup.get_controller_public_dns(old_controller_name)
    new_controller_public_dns = information_lookup.get_controller_public_dns(new_controller_name)
    command = " ssh -o StrictHostKeyChecking=no " + new_private_dns + " &>/dev/null << EOF"
    command += " \n sudo su - centos\n cd /var/www/aaam-atr-uiv2/config"
    command += " \n sed -i -e 's/samlRedirect=https:\/\/" +  old_domain_name.replace('/','\/') + "\/atr-" + old_domain_root_context + "\/auth\/saml/samlRedirect=https:\/\/" +  new_domain_name.replace('/','\/') + "\/atr-" + new_domain_root_context + "\/auth\/saml/g' applicationproperties.txt"
    command += " \n sed -i -e 's/url=amqp:\/\/admin:@cn@dm1n@" +  old_controller_public_dns + "\/aiam.VH/url=amqp:\/\/admin:@cn@dm1n@" +  new_controller_public_dns + "\/aiam.VH/g' applicationproperties-sec.txt"
    command += " \n cd /var/www/aaam-atr-uiv2/"
    command += " \n sudo forever start server.js"
    command += " \n docker start rundeck"
    command += " \n docker exec -it rundeck sed -i 's/grails.serverURL=https:\/\/" + old_domain_name.replace('/','\/') + "\/rundeck-" + old_domain_root_context + "/grails.serverURL=https:\/\/" + new_domain_name.replace('/','\/') + "\/rundeck-" + new_domain_root_context + "/g' /opt/rundeck/server/config/rundeck-config.properties"
    command += " \n docker restart rundeck"
    command += " \nEOF"
    os.system(command)

    

def migrate_instance(old_region, old_instance_id, aws_region_code, nodejs_db, old_base_order_id, new_region, environment, domain_context_root, old_access_url, sap_contract_id, project_id, customer_enterprise_id, old_controller_name, new_controller_name, all_app_orders):

    new_order_item_uid, new_access_url =  place_new_instace_order(nodejs_db, old_base_order_id, new_region, environment)
    new_aws_region_code = information_lookup.aws_region_code_lookup(new_region)
    sda1_snapshot_id, sdb_snapshot_id, sdc_snapshot_id = create_snapshots_from_old_instance(old_instance_id, aws_region_code, old_base_order_id)
    new_sda1_snapshot_id, new_sdb_snapshot_id, new_sdc_snapshot_id = copy_snapshots_to_new_region([sda1_snapshot_id, sdb_snapshot_id, sdc_snapshot_id], aws_region_code, new_aws_region_code, old_instance_id, old_base_order_id)
    new_volume_ids = create_volumes_from_snapshots([new_sda1_snapshot_id,new_sdb_snapshot_id, new_sdc_snapshot_id], new_aws_region_code, old_instance_id, new_region, domain_context_root)
    new_sda1_volume_id = new_volume_ids[0]
    new_sdb_volume_id = new_volume_ids[1]
    new_sdc_volume_id = new_volume_ids[2]
    wait_for_volume_completed_and_instnace_started([new_sda1_volume_id, new_sdb_volume_id, new_sdc_volume_id], new_order_item_uid, new_aws_region_code)
    new_instance_id, new_private_dns = get_new_instance_details(new_order_item_uid, new_aws_region_code)
    detach_volume_from_new_instance(new_instance_id, new_aws_region_code)	
    attach_new_volume(new_instance_id, new_aws_region_code, new_sda1_volume_id, 'sda1')
    attach_new_volume(new_instance_id, new_aws_region_code, new_sdb_volume_id, 'sdb')
    attach_new_volume(new_instance_id, new_aws_region_code, new_sdc_volume_id, 'sdc')
    start_instance(new_instance_id, new_aws_region_code)
    configure_and_start_splunk(new_private_dns, new_access_url)
    configure_apps(all_app_orders, new_private_dns, new_access_url, old_access_url, old_controller_name, new_controller_name)
    copy_controller_mongo(old_region, new_region, environment, sap_contract_id, project_id, customer_enterprise_id)
