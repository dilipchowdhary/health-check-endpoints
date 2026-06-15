import utils
from utils import requests_retry_session
from dateutil.parser import parse

class parsingJSON(object):
    pass

def __init__():
    pass



def getrespone(url):
    ret = requests_retry_session().get(url,timeout = 10)
    return ( ret.json() )


def getlaunchtime(ipaddr):
    orchestator_url = (utils.orchestrator+"%s" %(ipaddr))
    print (orchestator_url)
    data = getrespone(orchestator_url)
    for i in data['results']:
        #if (ip_add_string == ipaddr):
        if  (i["launch_time"]):
            dt = parse(i["launch_time"])
            return (dt.date())
               

 
