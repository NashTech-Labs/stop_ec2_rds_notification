import boto3 
import time

def lambda_handler(event, context):
    client_sns = boto3.client('sns')
    client = boto3.client('ec2') 
    id = boto3.client('sts').get_caller_identity().get('Account') 
    
    #------------------------lists for storing the info of ec2 and rds---------------------------------
    
    Flag=""
    S_no = []
    Account_ID = []
    Account_Name = []
    Service = []
    Instance_ID = []
    Instance_Name = []  
    Instance_Size = []
    Region = []
    Status = []
    ids = []
    s_no=0
    
     #------------------------------EC2-----------------------------------------------------------------
    
    ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    
    for region in ec2_regions:  
        ec2=boto3.client('ec2',region_name=region)
        x= ec2.describe_instances()
        for each in x['Reservations']:
            for i in each['Instances']:   
                if i['State']['Name'] == 'running': 
                    Flag =True
                    #------Remove the comment to stop the ec2 in 'running' state only
                    x=ec2.stop_instances(InstanceIds=[i['InstanceId']])   
                    Status.append("Stopped")                                # Status update
                    Account_Name.append("Devops")                           # UPDATE THE ACCOUNT NAME MANUALLY
                    Account_ID.append(id)
                    s_no = s_no+1
                    for t in i['Tags']:  
                        if t['Key'] == 'Name':                              #name
                            Instance_Name.append(t['Value'])
                        else:
                            Instance_Name.append(" ") 
                            break
                    Instance_ID.append(i['InstanceId'])                     #id
                    Instance_Size.append(i['InstanceType'])                 #type
                    Service.append("EC2")                                   #service
                    S_no.append(s_no)  
                    Region.append(i['Placement']['AvailabilityZone'])   
                        
    
    #-------------------------RDS---------------------------------------------------------------------
          
        
    for region in ec2_regions: 
        rds_client = boto3.client('rds',region_name=region)    
        instances = rds_client.describe_db_instances()
        for each in range(len(instances['DBInstances'])): 
            if instances['DBInstances'][each]['DBInstanceStatus'] == 'available' :
                Flag = True
                #------Remove the comment to stop the rds in available' state only
                response = rds_client.stop_db_instance(DBInstanceIdentifier = instances['DBInstances'][each]['DBInstanceIdentifier'] ) 
                Status.append("Stopped")                       #status update
                s_no = s_no+1
                Account_Name.append("Devops")                  # UPDATE THE ACCOUNT NAME MANUALLY    
                S_no.append(s_no) 
                Account_ID.append(id)
                Service.append("RDS")    
                Instance_Name.append(instances['DBInstances'][each]['DBInstanceIdentifier'])
                Instance_ID.append(instances['DBInstances'][each]['DbiResourceId'])
                Instance_Size.append(instances['DBInstances'][each]['DBInstanceClass'])   
                Region.append(instances['DBInstances'][each]['AvailabilityZone'])   
                
                
    #------------------------Table work--------------------------------------------------------------------------------   
         
    Tab_message = ""        
    Tab_message += "\n"
    Tab_message += "-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------" + "\n"
    Tab_message += "|{}{}{}{}{}{}{}{}{}".format('S no'.ljust(7," "), 'Account Id'.center(25," "),'Account Name'.center(25," "), 'Service'.center(10," "),'Name'.center(30," "), 'Service Id'.center(40," "),'Service Size'.center(40," "),'Region'.center(20," ") ,'Status'.rjust(20," ")) + "\n"
    Tab_message += "-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------" + "\n"
    
    # print(len(S_no))
    # print(Account_ID)
    # print(Account_Name)
    # print(Instance_Name)
    # print(Service)
    # print(Instance_ID)
    # print(Instance_Size)
    # print(Region)
    # print(Status)
    
    for i in range(len(S_no)):
        Tab_message += "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------" +"\n"
        Tab_message += "|{}{}{}{}{}{}{}{}{}".format(str(S_no[i]).ljust(7," "),str(Account_ID[i]).center(25," "),str(Account_Name[i]).center(25," "),str(Service[i]).center(10," "),str(Instance_Name[i]).center(30," ") , str(Instance_ID[i]).center(40," "), str(Instance_Size[i]).center(40," "), str(Region[i]).center(20," ") ,str(Status[i]).rjust(20," ")) + "\n"
        Tab_message += "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------" + "\n" 
    

            
    #-------------------------------message delivery work(table)--------------------------------------------------------------
    
       
                      
    if len(S_no)== 0 :     
        message =" No EC2 or RDS instances are running currently!!!"
        print(message)
        resp = client_sns.publish(TargetArn="arn::rds_ec2_info", Message=message, Subject="RDS and EC2 Detail")
    else:    
        message = ""   
        message += Tab_message
        resp = client_sns.publish(TargetArn="arn:", Message=message, Subject="RDS and EC2 Detail")   
        print(message) 
        
