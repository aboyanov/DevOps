import sys
import argparse
import base64
import migrate_instance
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from util_modules import information_lookup
from util_modules import util
from util_modules import get_order_information



logger = get_order_information.logger
def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('combination', help="combination of the order use wants to extned", type=str)
    parser.add_argument('access_url', help="access_url of the order use wants to extned", type=str)
    parser.add_argument('base_order_id', help="order_id of the order use wants to extned", type=str)
    parser.add_argument('new_region', help="order_id of the order use wants to extned", type=str)
    parser.add_argument('userepid', help="User Enterprise id who interacts with Chatbot", type=str)
    parser.add_argument('jobid', help="Excution id of rundeck instance", type=str)
    
    args = parser.parse_args(arguments)
    arg_list = args.combination.split(';')
    
    access_url = args.access_url
    base_order_id = args.base_order_id
    new_region = args.new_region
    auth_token = base64.encodestring("chatbot_user:chatbot_user")
    global userepid 
    userepid = args.userepid.split("@")[0]
    global base_order_id_g
    global job_id
    job_id = args.jobid

    
    if len(arg_list) == 5 and access_url == "undefined" and base_order_id == "undefined":
        try:
            sap_contract_id, platform_type, private_dns, old_base_order_id, product_id, old_instance_id, nodejs_db, old_region, environment, aws_region_code, domain_context_root, all_app_order_id, all_app_orders, client_name, data_hub_domain, data_hub_context, customer_enterprise_id, project_id, private_ip_address =  get_order_information.get_order_information(sap_contract_id = arg_list[0], project_id =  arg_list[1], customer_enterprise_id = arg_list[2], deployment_region = arg_list[3] ,platform_name = arg_list[4], access_url = None, base_order_id = None)
            
            if platform_type != "AAAM Dedicated Instance Platform":
                logger.critical("Can only migrate splunk instances")
                exit(1)
            util.check_user_permission(userepid, customer_enterprise_id, "migrate")
            
            util.check_if_domain_context_root_exists(base_order_id, new_region, domain_context_root, nodejs_db)
            new_controller_name = new_region + environment
            old_controller_name = old_region + environment
            old_access_url = "https://" + information_lookup.url_lookup(old_region, environment) + "/" + domain_context_root
            
            migrate_instance.migrate_instance(old_region, old_instance_id, aws_region_code, nodejs_db, old_base_order_id, new_region, environment, domain_context_root, old_access_url, sap_contract_id, project_id, customer_enterprise_id, old_controller_name, new_controller_name, all_app_orders)
        except Exception as e:
            print e
            logger.critical("Job failed!")
            exit(1)
        logger.info("OrderItemUId : " + base_order_id_g + " JobStatus : Job succeeded!")
    
    
    elif access_url != "undefined":
        try:
            try:
                access_url = access_url.split("/")
                if access_url[3] == "dh" or access_url[3] == "myWizarddh" or access_url[3] == "myWizard-dataHub" or access_url[3] == "dhuat01" or access_url[3] == "dhuat02":
                    logger.critical("Cannot migrate Managed Instance")
                    exit(1) 
                access_url = "/".join([access_url[0], access_url[1], access_url[2], access_url[3]])
            except Exception as e:
                logger.critical("Not a valid URL")
                raise e
                
            sap_contract_id, platform_type, private_dns, old_base_order_id, product_id, old_instance_id, nodejs_db, old_region, environment, aws_region_code, domain_context_root, all_app_order_id, all_app_orders, client_name, data_hub_domain, data_hub_context, customer_enterprise_id, project_id, private_ip_address =  get_order_information.get_order_information(sap_contract_id = None, project_id = None, customer_enterprise_id = None,deployment_region = None, platform_name = None, access_url = access_url, base_order_id = None)
            
            if platform_type != "AAAM Dedicated Instance Platform":
                logger.critical("Can only migrate splunk instances")
                exit(1)
                
            util.check_user_permission(userepid, customer_enterprise_id, "migrate")
            base_order_id_g = base_order_id
            util.check_if_domain_context_root_exists(base_order_id, new_region, domain_context_root, nodejs_db)
            new_controller_name = new_region + environment
            old_controller_name = old_region + environment
            
            old_access_url = "https://" + information_lookup.url_lookup(old_region, environment) + "/" + domain_context_root
            migrate_instance.migrate_instance(old_region, old_instance_id, aws_region_code, nodejs_db, old_base_order_id, new_region, environment, domain_context_root, old_access_url, sap_contract_id, project_id, customer_enterprise_id, old_controller_name, new_controller_name, all_app_orders)
           
        except Exception as e:
            print e
            logger.critical("Job failed!")
            exit(1)
        logger.info("OrderItemUId : " + base_order_id_g + " JobStatus : Job succeeded!")

    elif base_order_id != "undefined":
        base_order_ids = base_order_id.split(";")
        for base_order_id in base_order_ids:
            try:
                
                base_order_id_g = base_order_id
                sap_contract_id, platform_type, private_dns, old_base_order_id, product_id, old_instance_id, nodejs_db, old_region, environment, aws_region_code, domain_context_root, all_app_order_id, all_app_orders, client_name, data_hub_domain, data_hub_context, customer_enterprise_id, project_id, private_ip_address =  get_order_information.get_order_information(sap_contract_id = None, project_id = None, customer_enterprise_id = None, deployment_region = None, platform_name = None, access_url = None, base_order_id = base_order_id)
                
                if platform_type != "AAAM Dedicated Instance Platform":
                    logger.critical("Can only migrate splunk instances")
                    exit(1)
                    
                util.check_user_permission(userepid, customer_enterprise_id, "migrate")
                util.check_if_domain_context_root_exists(base_order_id, new_region, domain_context_root, nodejs_db)
                new_controller_name = new_region + environment
                old_controller_name = old_region + environment
                old_access_url = "https://" + information_lookup.url_lookup(old_region, environment) + "/" + domain_context_root
                
                migrate_instance.migrate_instance(old_region, old_instance_id, aws_region_code, nodejs_db, old_base_order_id, new_region, environment, domain_context_root, old_access_url, sap_contract_id, project_id, customer_enterprise_id, old_controller_name, new_controller_name, all_app_orders)
               
            except Exception as e:
                print e
                logger.critical("Job failed!")
                exit(1)
            logger.info("OrderItemUId : " + base_order_id_g + " JobStatus : Job succeeded!")
    else:
        logger.critical("Please supply correct augrments!")
        exit(1)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
