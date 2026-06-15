# -*- coding: utf-8 -*-

import utils
import csv
from utils  import get_line_content
from utils  import compare_status
from datetime import datetime
from  parsingJSON import getlaunchtime


class report_utils(object):
    pass
def __init__(sel):
    pass

PREVIOUS_OLD_DATE=utils.get_pervious_system_time(7)
TWO_WEEKS_OLD_DATE=utils.get_pervious_system_time(30)


def get_status_date(rvar,old_date):
    previous_time = get_previous_record_content(rvar['env_out_file'],old_date)
    date_time = []
    with open(rvar['env_out_file'],'r') as _filename:
        if ((previous_time is None) or (previous_time == "") or (previous_time == "None")):
            previous_record_status = "DOWN"
            previous_record_date = old_date
        else:
            previous_record = get_line_content(_filename,previous_time)
            previous_record_status = previous_record.split(",")[1].strip()
            previous_record_date = previous_record.split(",")[0].strip()
    date_time.append(previous_record_status)
    date_time.append(previous_record_date)
    return date_time

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d %H")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def generate_report_content(rvar):
    with open(rvar['env_out_file'],'r') as _filename:
        current_record=get_line_content(_filename,rvar['CURRENT_TIME'])
        current_record_status = current_record.split(",")[1].strip()
        current_record_date = current_record.split(",")[0].strip()
        env_name = current_record.split(",")[2].strip()
        recent_week_status = get_status_date(rvar,PREVIOUS_OLD_DATE)
        p_rece_week = get_status_date(rvar,TWO_WEEKS_OLD_DATE)
        recomd_termination = compare_status(current_record_status,recent_week_status[0],p_rece_week[0])
        ip_addr = utils.get_ip_addr(rvar['HOSTNAME'])
        #ip_addr = "10.74.161.157"
        ec2_launch_date = getlaunchtime(ip_addr)
        ec2_age = (days_between(rvar['CURRENT_TIME'],str(ec2_launch_date)))
        outfilestring = (env_name+","+current_record_date+","+current_record_status+","+recent_week_status[0]+","+p_rece_week[0]+","+ip_addr.rstrip()+","+str(ec2_age)+","+recomd_termination)#
        utils.writeToReportfile(outfilestring,rvar['REPORT_FILE'])
    
def get_previous_record_content(filename,old_time):
    old_record = None
    filter_date = {}
    n = []
    old_record_date = old_time.split(" ")[0]
    old_record_hour = old_time.split(" ")[1]
    with open(filename,'r') as _filename:
        reader = csv.reader(_filename, delimiter=",")
        _list = list(reader)
        filtereelist = utils.uniquelist(_list)
        for i in filtereelist:
            date = i.split(" ")[0]
            hour = i.split(" ")[1]
            filter_date.setdefault(date, [])
            if date in filter_date:
                filter_date[date].append(str(hour))
            else:
                filter_date[date] = str(hour)
        if old_record_date in filter_date:
            for i in filter_date[old_record_date]:
                if (i < old_record_hour):
                     n.append(i)
            max_hour = (i)
            old_record = old_record_date+" "+max_hour
        else:
            old_record = None
        return old_record

