# -*- coding: utf-8 -*-
import os
import datetime
import subprocess
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import re
import boto3
from botocore.config import Config

try:
    requests.packages.urllib3.disable_warnings()
except AttributeError as ar:
    pass


class utils(object):
    pass
def __init__(sel):
    pass



orchestrator = "https://orchestra.ebiz.verizon.com/aws/api/instance/?platform=linux&region=us-east-1&environment=NONPROD&vsad=BPHV&format=json&search="
headers = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

proxie_defination = {
 'http': 'http://proxy.ebiz.verizon.com:80',
 'https': 'http://proxy.ebiz.verizon.com:80',
 'no_proxy': '127.0.0.1,localhost,instance-data,169.254.169.254,.elb.amazonaws.com,.verizon.com,.ebiz.verizon.com,oneartifactory.verizon.com '
}

pno_res_keys = ['Implementation-Version','Implementation-Title','Implementation-Title','Implementation-Vendor-Id','COMMIT_ID']
res_keys = ['version','artifact','name','time','group','COMMIT_ID','git-commit-info']
def regexString (apptype):
    if (apptype == "PRE"):
        regexstring = "PRE\sbuild"
    elif (apptype == "RDS"):
        regexstring = "RDS\sbuild"
    return regexstring

def get_instance_ips_from_asg(asg_name, region_name):

    ec2_client = boto3.client('ec2', region_name=region_name,config=Config(proxies=proxie_defination))
    asg_client = boto3.client('autoscaling', region_name=region_name,config=Config(proxies=proxie_defination))

    # Get the instance IDs of instances in the Auto Scaling Group
    response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    instance_ids = [instance['InstanceId'] for instance in response['AutoScalingGroups'][0]['Instances']]

    # Get the IP addresses of instances
    ips = []
    if instance_ids:
        response = ec2_client.describe_instances(InstanceIds=instance_ids)
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                ips.append(instance['PrivateIpAddress'])

    return ips

def load_url_for_nebula(instance_ips,protocal,ports,path,ENV_INDEX,ENV_NAME):
    listofurls=[]
    portlist = ports.split(":")
    for port in portlist:
        for instance in instance_ips:
            healthcheck_url=protocal+"://"+instance+":"+port+path+","+ENV_INDEX+","+ENV_NAME
            listofurls.append(healthcheck_url)
    return listofurls

def check_tmp_directory(tmp_dir):
    if not os.path.exists(tmp_dir):
        access_rights = 0o755
        try:
            os.mkdir(tmp_dir,access_rights)
        except OSError:
            print ("Creation of the directory %s failed" % tmp_dir)
        else:
            print ("Successfully created the directory %s" % tmp_dir)


def touch(file):
    file_exists = os.path.exists(file)
    if file_exists:
        print ("file already existing... Skipping touch function")
    else:
        print ("files not existed,creating a new file")
        newfile = open(file,'a')
        newfile.close()

def uniquelist(filecont):
    fname = []
    for row in filecont:
        if row[0] not in fname:
            fname.append(row[0])
    return fname

def get_domain_name (url):
    domain = url.split("://")[1].split("/")[0].split('.')[0]
    print ("Getting HOSTNAME/ENV NAME  from the url <<<< %s " % (url))
    return domain

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    time.sleep(5)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_system_time():
    current_time =datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    return current_time

def get_pervious_system_time(numofdays):
    Previous_Date = datetime.datetime.now() - datetime.timedelta(days=numofdays)
    Previous_Date_Formatted = Previous_Date.strftime ('%Y-%m-%d %H')
    return Previous_Date_Formatted

def remove_lines(filename):
    print ("Removing lines if greater than 30days from file %s \n" %(filename))
    cmd = "sed -i 720q %s" % (filename)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()

def load_filecontent(filename,check_type,comment_char='#'):
    props = []
    with open(filename, "r") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):

                if (len(l.split(','))) == 7:
                    instance_ips=get_instance_ips_from_asg(l.split(",")[0],l.split(",")[1])
                    if instance_ips :
                        listofurls=load_url_for_nebula(instance_ips,l.split(",")[2],l.split(",")[3],l.split(",")[4],l.split(",")[5],l.split(",")[6])
                        props.extend(listofurls)
                else:
                    props.append(l)
    return props

def get_line_content(filename,content_starts):
    for line in filename:
        if (line.startswith(content_starts)):
            return line

def writeTooutfile(filename,content):
    check_tmp_directory(os.path.dirname(filename))
    touch(filename)
    with open(filename,'r+') as _filename:
        data =  _filename.read()
        _filename.seek(0, 0)
        _filename.write(content.rstrip('\r\n') + "\n"+data)
    remove_lines(filename)


def writeToReportfile(content,reportfile):
    with open(reportfile,'a+') as _filename:
        _filename.write(content.rstrip('\r\n')+"\n")

def sort_file_content(reportfile):
    with open(reportfile, 'r+') as file:
        lines = file.readlines()
        sorted_lines = sorted(lines,key= lambda x: x.split(",")[2])
        sorted_lines1 = sorted(sorted_lines,key= lambda x: x.split(",")[0])
        file.truncate()
        file.seek(0)
        file.writelines(sorted_lines1)
        


def getDvsVersion (url):
    _url = url.rpartition("/")[0]
    finalurl = _url + "/versionDetails.properties"
    try:
        ret = requests_retry_session().get(finalurl,timeout = 5,verify=False)
    except  (requests.exceptions.RetryError or requests.Timeout):
        ret = 500
    if (ret == 500):
        response = "DOWN"
    else:
        response = 'UP' if ret.ok in [200, 201] or ret.ok == True else "DOWN"
    if (response == 'UP'):
        _response_content = ret.text
        _response_content.rstrip()
        pattern = r"(\d+\.\d+/\d+)"
        match = re.search(pattern,_response_content)
        if match:
            _response_content = match.group(1)
            response_content = _response_content
        else:
            response_content = "Version Not Found"
    else:
        response_content = "N/A"
    return response_content

def getDVSCommitId(url):
    finalurl = url
    try:
        ret = requests_retry_session().get(finalurl,timeout = 5,verify=False)
    except  (requests.exceptions.RetryError or requests.Timeout):
        ret = 500
    if (ret == 500):
        response = "DOWN"
    else:
        response = 'UP' if ret.ok in [200, 201] or ret.ok == True else "DOWN"
    if (response == 'UP'):
        _response_content = ret.text
        body_match = re.search(r'<body[^>]*>(.*?)</body>', _response_content, re.IGNORECASE | re.DOTALL)
        if body_match:
            body_content = body_match.group(1).strip()
            commitMatch = re.search(r'Git Commit ID:\s*(\w+)', body_content)
            if commitMatch:
                response_content = commitMatch.group(1)
        else:
            response_content = "COMMIT_ID NOT FOUND"
    else:
        response_content = "N/A"
    return response_content
            
def getDVSStartTime(url):
    finalurl = url
    try:
        ret = requests_retry_session().get(finalurl,timeout = 5,verify=False)
    except  (requests.exceptions.RetryError or requests.Timeout):
        ret = 500
    if (ret == 500):
        response = "DOWN"
    else:
        response = 'UP' if ret.ok in [200, 201] or ret.ok == True else "DOWN"
    if (response == 'UP'):
        _response_content = ret.text
        body_match = re.search(r'<body[^>]*>(.*?)</body>', _response_content, re.IGNORECASE | re.DOTALL)
        if body_match:
            body_content = body_match.group(1).strip()
            commitMatch = re.search(r'Startup Time:\s*(.+)', body_content)
            if commitMatch:
                response_content = commitMatch.group(1)
        else:
            response_content = "START TIME NOT FOUND"
    else:
        response_content = "N/A"
    return response_content


def compare_status(current_record_status,recent_week_status,p_rece_week):
    status = "DOWN"
    if ((current_record_status == status) and (recent_week_status == status ) and (p_rece_week == status )):
        overall_status = "Yes"
    else:
        overall_status = "No"
    return overall_status

def get_target_group_health(target_group_arn, region_name):
    elbv2_client = boto3.client('elbv2', region_name=region_name, config=Config(proxies=proxie_defination))

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
        'healthy': len(healthy_targets),
        'unhealthy': len(unhealthy_targets),
        'total_targets' : len(total_targets),
    }

def get_ip_addr(ip_add_show):
    cmd = "/usr/bin/dig +short "+ip_add_show
    _line = ""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout:
        _line = line
        process.wait()
    return _line

def searchcontentstring(content,regstring):
    my_log_lst = content.splitlines()
    matchstring = "N/A"
    for i in my_log_lst:
        line= re.findall(regstring, i);
        if line:
         matchstring = (i.strip())
    return matchstring

def get_health(url,apptype):
    ret_response = {}
    try:
        ret = requests_retry_session().get(url,timeout = 5,verify=False)
    except  (requests.exceptions.RetryError or requests.Timeout):
        ret = 500
    except  (requests.exceptions.ConnectionError):
        ret = 500
    if (ret == 500):
        ret_response['resp_state'] = "DOWN"
        for des_key in res_keys:
            ret_response[des_key] = "Not Found"
    else:
        response = 'UP' if ret.ok in [200, 201] or ret.ok == True else "DOWN"
        ret_response['resp_state'] = response
        if ((apptype != "PRE") and (apptype != "RDS") and (apptype != "REALTIME") and (apptype != "CACHE-PNO")):
            if (response == "UP"):
                if ((ret.headers.get("content-type") != "application/xml") and (ret.headers.get("content-type") != "text/html;charset=UTF-8")):
                    response_content = ret.json()
                    if 'build' in response_content:
                        for des_key in res_keys:
                            if des_key in response_content['build']:
                                ret_response[des_key] = response_content['build'][des_key]
                                if 'git-commit-info' in response_content['build']:
                                    ret_response['COMMIT_ID'] = response_content['build']['git-commit-info']
                            else:
                                ret_response[des_key] = "Not Found"
                    elif 'results' in response_content:
                        ret_response['time'] = response_content['results']['Start-time']
                        for des_key in pno_res_keys:
                            if des_key in response_content['results']['Manifest']['mainAttributes']:
                                ret_response[des_key] = response_content['results']['Manifest']['mainAttributes'][des_key]
                            else:
                                ret_response[des_key] = "Not Found"
                    else:
                        if 'serviceStartTime' in response_content:
                            ret_response['time'] = response_content['serviceStartTime']
                        elif 'Service Start Time' in response_content:
                            ret_response['time'] = response_content['Service Start Time']
                        elif 'startUpTime' in response_content:
                            ret_response['time'] = response_content['startUpTime']
                        elif 'Time' in response_content:
                            ret_response['time'] = response_content['Time']
                        else:
                            ret_response['time'] = "N/A"
                        if 'version' in response_content:
                            ret_response['version'] = response_content['version']
                        elif 'Version' in response_content:
                            ret_response['version'] = response_content['Version']
                        elif 'buildNumber' in response_content:
                            portinfo = response_content['port'].replace(",","-")
                            ret_response['version'] = portinfo+":"+response_content['buildNumber']
                        else:
                            ret_response['version'] = "N/A"
                        if 'commitId' in response_content:
                            ret_response['COMMIT_ID'] = response_content['commitId']
                        elif 'Commit Id' in response_content:
                            ret_response['COMMIT_ID'] = response_content['Commit Id']
                        elif '' in response_content:
                            ret_response['COMMIT_ID'] = response_content['git-commit-info']
                        elif 'gitCommitId' in response_content:
                            ret_response['COMMIT_ID'] = response_content['gitCommitId']
                        else:
                            ret_response['COMMIT_ID'] = "N/A"
                else:
                    ret_response['time'] = "N/A"
                    ret_response['version'] = "N/A"
                    ret_response['COMMIT_ID'] = "N/A"
            else:
                for des_key in res_keys:
                    ret_response[des_key] = "Not Found"
            if 'Implementation-Version' in ret_response:
                ret_response['version'] = ret_response['Implementation-Version']
            if (type(ret_response['time'])) == dict:
                newTime = ret_response['time']['epochSecond']
                NewTimeResponse = datetime.datetime.fromtimestamp(newTime).strftime('%Y-%m-%d %H:%M:%S')
                ret_response['time'] = NewTimeResponse
        else:
            if (response == "UP"):
                regexstring = apptype+"\sbuild"
                response_content = ret.text
                ret_response['time'] = "N/A"
                ret_response['version'] = searchcontentstring(response_content,regexstring)
                if ((ret_response['version'] == "N/A") and (apptype == "PRE")):
                    ret_response['version'] = getDvsVersion(url)
                if url.endswith('Info.jsp'):
                    ret_response['COMMIT_ID'] = getDVSCommitId(url)
                    ret_response['time'] = getDVSStartTime(url)
                else:
                    ret_response['COMMIT_ID'] = "N/A"
            else:
                ret_response['time'] = "N/A"
                ret_response['version'] = "Not Found"
                ret_response['COMMIT_ID'] = "N/A"
    return ret_response
