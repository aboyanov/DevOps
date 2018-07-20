import boto3
import json
import sys
from datetime import datetime, timedelta
import time

def main():
    try:
        scope_regions = ['ap-southeast-1' , 'ap-southeast-2', 'ap-northeast-1','eu-west-1','us-east-1','eu-central-1']
        my_session = boto3.Session(profile_name='default')
        current_date = datetime.now()
        cutoff_date = current_date - timedelta(days=10)
        cutoff_date = cutoff_date.strftime('%d/%m/%Y')
        v_ChatbotStoppedDate = current_date
        print "Cutoff Date is:"+str(cutoff_date)
##Iterate through each region
        for my_region in scope_regions:
            if my_region == 'ap-southeast-1':
               v_region_name =  'singapore'
            elif my_region == 'ap-southeast-2':
               v_region_name = 'sydney'
            elif my_region == 'eu-central-1':
               v_region_name =  'frankfurt'
            elif my_region == 'us-east-1':
               v_region_name =  'virginia'
            elif my_region == 'ap-northeast-1':
               v_region_name =  'tokyo'
            elif my_region == 'eu-west-1':
               v_region_name = 'ireland'
            print "Region: "+v_region_name
            terminate_flag = False
            ##Get Instances which was stopped by chatbot
            try:
                   ec2 = my_session.client('ec2', region_name=my_region)
                   inst_details = ec2.describe_instances(Filters=[{"Name":"instance-state-name","Values":["stopped"]},{"Name":"tag:chatbot_terminated_status","Values":["Termination initiated via Chatbot by*"]}])

                   for ins in inst_details['Reservations']:
                       try:				   
                             for j in ins['Instances']:
                                 details = (j['Tags'])
                                 v_instance_state = j['State']['Name']
                                 v_instance_id = (j['InstanceId'])
                                 v_ChatbotStoppedDate = ""
                                 v_ChatbotStoppedDate_str = ""
                                 v_ChatbotStoppedDate_str = [obj for obj in details if(obj['Key']=='chatbot_terminated_date')] 
                                 v_ChatbotStoppedDate = v_ChatbotStoppedDate_str[0]['Value']
#                                 print "chatbot Stopped date is:" + str(v_ChatbotStoppedDate)
#                                 print v_instance_id
                             ##Compare Chatbot Stopped Date then terminate the Instance
                             if  datetime.strptime(cutoff_date, "%d/%m/%Y") > datetime.strptime(v_ChatbotStoppedDate, "%d/%m/%Y"):
                                 print "Terminating Instance :"+v_instance_id+" which was Stopped by Chatbot on:"+v_ChatbotStoppedDate
                                 terminate_flag = True
                                 response = ec2.terminate_instances(InstanceIds=[v_instance_id,],)
                             
                             ##If instance terminated find ELB details
                             if terminate_flag == True:
                                elb_client = my_session.client('elb',region_name=my_region)
                                response = elb_client.describe_load_balancers()
                                for i in response['LoadBalancerDescriptions']:
                                    try:
                                       inst1 = i['Instances']
                                       v_elb_attached_inst_count = len(inst1)
                                       for aws_inst in i['Instances']:
                                           for key1 in  aws_inst:
                             
                                               elb_instance = aws_inst[key1]
                                               if elb_instance == v_instance_id :
                                                  print str(v_elb_attached_inst_count) + " Instances attached  in ELB "+ i['LoadBalancerName']
                             
                                                  ##Delete ELB If ELB has single terminated instance attached to it
                                                  if elb_instance == v_instance_id and (v_elb_attached_inst_count == 1):
                                                     print "Deleting ELB :"+i['LoadBalancerName']
                                                     elb_delete = elb_client.delete_load_balancer(LoadBalancerName=i['LoadBalancerName'])
#                                                     elb_create_tag = elb_client.add_tags(LoadBalancerNames=[i['LoadBalancerName'],], Tags=[{'Key': 'Delete ELB Status','Value': 'ELB flagged for deleting'},])
                             
                                                  ##Deregister instance from ELB If ELB multiple instance attached to it
                                                  elif elb_instance == v_instance_id and (v_elb_attached_inst_count > 1):
                                                     print "Deregistering Instance : "+elb_instance+" from ELB: "+i['LoadBalancerName']
                                                     elb_deregister_instance = elb_client.deregister_instances_from_load_balancer(LoadBalancerName=i['LoadBalancerName'],Instances=[{'InstanceId': elb_instance },])
#                                                     elb_create_tag = elb_client.add_tags(LoadBalancerNames=[i['LoadBalancerName'],], Tags=[{'Key': 'Deregister Instance','Value': 'Deregister an Instance'},])
                                                     v_elb_attached_inst_count = v_elb_attached_inst_count - 1
                             
                                    except IndexError:
                                            print "No Instances defined for the ELB"
                       except  IndexError, err:
                              print "Proper tag not created for the instance "+ v_instance_id					
                       except  Exception, e:
                              print str(e)					 	  
            except  IndexError, err:
                    print "Proper tag not created for the instance "+ v_instance_id					
            except  Exception, e:
                    print str(e)
    except  Exception, e:
        print str(e)



if __name__ == '__main__':
    main()