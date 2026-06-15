import os
import sys
import csvtoHTML
import utils
import argparse
import report_utils
from utils import writeTooutfile
from utils  import get_domain_name
from utils import get_health
from utils import load_filecontent
from utils import writeToReportfile
from utils import check_tmp_directory
from utils import get_target_group_health
from concurrent.futures import ThreadPoolExecutor
import time



def validate_commands(cli_options):
    if cli_options.urlfile is None:
        raise Exception("ERROR: Missing -f [file]")
    if cli_options.apptype is None:
        raise Exception("ERROR: Missing -at [PNO,MS]")
    if cli_options.report is None:
        cli_options.report = "report_file.html"
    if cli_options.checktype is None:
        cli_options.checktype = "healthcheck"
    if cli_options.tmpdir is None:
        cli_options.tmpdir = os.path.join(os.getcwd(), "tmp")
    else:
        cli_options.tmpdir = os.path.abspath(cli_options.tmpdir)

def divide_chunks(urllist, n):
    for i in range(0, len(urllist), n): 
        yield urllist[i:i + n]        


def get_url_response(load_url):
    #for load_url in load_urls_list:
    rvar = {}
    url = load_url.split(",")[0]
    rvar['REPORT_FILE'] = os.environ["report_file"]
    rvar['SERVICE_URL'] = url
    rvar['ENV_INDEX']=load_url.split(",")[2]
    rvar['ENV_NAME']=get_domain_name(url)
    rvar['URL_RESPONSE']=get_health(url,os.environ["apptype"])
    rvar['HEALTH_STATUS']=rvar['URL_RESPONSE']['resp_state']
    rvar['VERSION']=rvar['URL_RESPONSE']['version']
    rvar['ARTIFACT_NAME']=load_url.split(",")[1]
    rvar['JVM_START_TIME']=rvar['URL_RESPONSE']['time']
    rvar['env_out_file'] = os.path.join(os.environ["tmp_dir"],rvar['ENV_NAME']+'.csv')
    rvar['CURRENT_TIME'] = utils.get_system_time()
    rvar['COMMIT_ID'] = rvar['URL_RESPONSE']['COMMIT_ID']
    content=rvar['ENV_INDEX']+","+rvar['ARTIFACT_NAME']+","+rvar['SERVICE_URL']+","+rvar['HEALTH_STATUS']+","+rvar['JVM_START_TIME']+","+rvar['VERSION']+","+rvar['COMMIT_ID']+"\n"
    #writeTooutfile(rvar['env_out_file'],content)
    utils.writeToReportfile(content,rvar['REPORT_FILE'])
def main(__argv):
    # Building the command line options for ucontrol
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--urlfile', required=True, action="store",
                        help='Deployment descriptor file in JSON format (required)')
    parser.add_argument('-o', '--output', action='store',
                               help='Alternate output filename (optional)')
    parser.add_argument('-r', '--report', action='store',
                               help='Alternate reportfile (optional)')
    parser.add_argument('-t', '--tmpdir', action='store',
                               help='Alternate tmpdirectory to store data (optional)')
    parser.add_argument('-ct', '--checktype', action='store',
                               help='Alternate tmpdirectory to store data (optional)')
    parser.add_argument('-at', '--apptype', required=True, action="store",
                               help='application type based on response')
    cli_options = parser.parse_args(__argv)
    validate_commands(cli_options)
    sys.stdout.write("python main.py -f %s -r %s -t %s -at %s" % (cli_options.urlfile,cli_options.report,cli_options.tmpdir,cli_options.apptype))
    load_urls_list = load_filecontent(cli_options.urlfile,cli_options.checktype)
    tmp_dir = cli_options.tmpdir

    report_file = os.path.join(cli_options.tmpdir,'outfile.csv')
    os.environ["report_file"] = report_file
    os.environ["apptype"] = cli_options.apptype
    os.environ["tmp_dir"] = tmp_dir

    rvar = {}
    check_tmp_directory(os.path.join(tmp_dir))
    try:
        os.remove(report_file)
    except OSError:
        pass
    if (cli_options.checktype != "LB_CHECK"):
        header_string = '<th>ENV_INDEX</th> \n <th>ARTIFACT_NAME</th> \n <th>SERVICE_URL</th> \n <th>HEALTH_STATUS</th> \n <th>JVM_START_TIME</th> \n <th>VERSION</th> \n <th>COMMIT_ID</th>'
        #t1 = time.perf_counter()
        with ThreadPoolExecutor(15) as executor:
            # Force evaluation so worker exceptions are raised in the main thread.
            list(executor.map(get_url_response, load_urls_list))
        #t2 = time.perf_counter()
        #print(f'MultiThreaded Code Took:{t2 - t1} seconds')         
        
    else:
        for load_url in load_urls_list:
            rvar = {}
            rvar['REPORT_FILE'] = report_file
            rvar['ARTIFACT_NAME']=load_url.split(",")[0]
            rvar['ALB_ARN_TG']=load_url.split(",")[1]
            rvar['ALB_REGION']=load_url.split(",")[2]
            rvar['DESIRED_COUNT']=load_url.split(",")[3]
            rvar['ALB_HEALTH']=get_target_group_health(rvar['ALB_ARN_TG'],rvar['ALB_REGION'])
            rvar['HEALTHY_TARGETS']=rvar['ALB_HEALTH']['healthy']
            rvar['UNHEALTHY_TARGETS']=rvar['ALB_HEALTH']['unhealthy']
            rvar['TOTAL_TARGET']=rvar['ALB_HEALTH']['total_targets']
            header_string = '<th>APP_NAME</th> \n <th>REGION</th> \n <th>HEALTHY_TARGETS</th> \n <th>UNHEALTHY_TARGETS</th> \n <th>TOTAL_TARGET</th>\n <th>DESIRED_COUNT</th>'
            content=rvar['ARTIFACT_NAME']+","+rvar['ALB_REGION']+","+str(rvar['HEALTHY_TARGETS'])+","+str(rvar['UNHEALTHY_TARGETS'])+","+str(rvar['TOTAL_TARGET'])+","+str(rvar['DESIRED_COUNT'])+"\n"
            utils.writeToReportfile(content,rvar['REPORT_FILE'])


    utils.sort_file_content(report_file)
    csvtoHTML.html_codeToHTML(report_file,cli_options.report,header_string)


if __name__ == '__main__':
     __args = sys.argv[1:]
     main(__args)
