import boto3
from botocore.config import Config

def load_filecontent(filename,comment_char='#'):
    props = []
    with open(filename, "r") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):
               if (len(l.split(','))) == 6:
                   instance_ips=get_instance_ips_from_asg(l.split(",")[0],l.split(",")[1])
                   if instance_ips :
                       listofurls=load_url_for_nebula(instance_ips,l.split(",")[2],l.split(",")[3],l.split(",")[4],l.split(",")[5])
                       props.extend(listofurls)
               else:
                   props.append(l)
    return props

def load_url_for_nebula(instance_ips,ports,path,ENV_INDEX,ENV_NAME):
    listofurls=[]
    for port in ports:
        for instance in instance_ips:
            healthcheck_url="http://"+instance+":"+port+path+","+ENV_INDEX+","+ENV_NAME
            listofurls.append(healthcheck_url)
    return listofurls


def get_instance_ips_from_asg(asg_name, region_name):
    proxies = {
     'http': 'http://proxy.ebiz.verizon.com:80',
     'https': 'http://proxy.ebiz.verizon.com:80',
    }


    ec2_client = boto3.client('ec2', region_name=region_name,config=Config(proxies))
    asg_client = boto3.client('autoscaling', region_name=region_name,config=Config(proxies))

    # Get the instance IDs of instances in the Auto Scaling Group
    response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    instance_ids = [instance['InstanceId'] for instance in response['AutoScalingGroups'][0]['Instances']]

    # Get the IP addresses of instances
    ips = []
    if instance_ids:
        response = ec2_client.describe_instances(InstanceIds=instance_ids)
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                ips.append(instance['PrivateIpAddress'])  # Change to 'PublicIpAddress' if you need public IPs

    return ips

# asg_name = 'vzw-dagv-np-cxp-pno-ditamr23141-AutoScalingGroup2-I5eIx0eurzII'
# region_name = 'us-east-1'
# instance_ips = get_instance_ips_from_asg(asg_name, region_name)
# print("Instance IP addresses:", instance_ips)

load_filecontent('urlfile/urlslist.txt')

#---
#---
import boto3

def get_target_group_health(target_group_arn, region_name):
    """
    Get information about the health of targets registered with the specified target group.

    :param target_group_arn: ARN of the target group.
    :param region_name: AWS region name where the target group exists.
    :return: Dictionary containing information about healthy and unhealthy targets.
    """
    elbv2_client = boto3.client('elbv2', region_name=region_name)

    # Get target health information
    response = elbv2_client.describe_target_health(TargetGroupArn=target_group_arn)

    healthy_targets = []
    unhealthy_targets = []
    total_targets = []

    # Process target health information
    for target_health in response['TargetHealthDescriptions']:
        target_id = target_health['Target']['Id']
        total_targets.append(target_id)
        target_health_state = target_health['TargetHealth']['State']

        if target_health_state == 'healthy':
            healthy_targets.append(target_id)
        else :
            unhealthy_targets.append(target_id)

    return {
        'healthy': healthy_targets,
        'unhealthy': unhealthy_targets,
        'total_targets' : total_targets,
    }

# Example usage:
target_group_arn = 'arn:aws:elasticloadbalancing:us-west-2:128067331242:targetgroup/VZW-DAGV-CXPPNOB2C-ALB-TG/e2e0f4739a732544'
region_name = 'us-west-2'
target_health_info = get_target_group_health(target_group_arn, region_name)
#print(len(response['InstanceStates']))
#print(type(target_health_info['healthy']))
#print(len(target_health_info['healthy']))
print("Healthy targets:", len(target_health_info['healthy']))
print("Unhealthy targets:", len(target_health_info['unhealthy']))
print("total targets:" , len(target_health_info['total_targets']))
#print("unused targets:" ,len(target_health_info['unused']))
