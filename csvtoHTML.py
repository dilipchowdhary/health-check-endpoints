# -*- coding: utf-8 -*-
from utils import get_system_time

class csvtoHTML(object):
    pass
def __init__(sel):
    pass
def ConvertToHtml(csvreport,header_string):
    CUR_TIME =get_system_time()
    with open(csvreport, "r") as csvfile:
        lines = csvfile.readlines()

        b = []
        b.append('''
        <head>
            <style>
                table{
                    width: Auto;
                    table-layout:fixed;
                    colour:#b3d4fc;
                }
                td,th {
                    padding:5px;
                    border-bottom: 1px solid #ccc;
                }
                th{
                    background-color:#ccc;
                }
                tr{
                    background:#f7f7f7;
                }
                li {
                	  text-align: right;
                }
            </style>
        </head>
        <li>This report  generated at time: '''+CUR_TIME+'''  </li>
        <table>
        <tr>
        ''')
        #b.append("<th>ENV_INDEX</th> \n <th>ARTIFACT_NAME</th> \n <th>SERVICE_URL</th> \n <th>HEALTH_STATUS</th> \n <th>JVM_START_TIME</th> \n <th>VERSION</th>"+"\n")
        b.append(header_string)
        for line in lines:
            headerfields = line.split(",")
            b.append("<tr>" + "\n")
            for headers in headerfields:
                if (headers.strip() == "UP"):
                    b.append("<td align ='center' style='color:green'>"+headers.strip()+"</td>"+ "\n")
                elif (headers.strip() == "DOWN"):
                    b.append("<td align ='center' style='color:red'>"+headers.strip()+"</td>"+ "\n")
                else:
                    b.append("<td align ='center'>"+headers.strip()+"</td>"+ "\n")
            b.append("</tr>" + "\n")
        b.append('''
        </table>
        </body>
        </html>
        ''')
        c = "".join(b)
        return c

def html_codeToHTML(csvreport,reportfile,header_string):
    html_code = ConvertToHtml(csvreport,header_string)
    print ("Generating HTML repot content as file %s" %(reportfile))
    with open(reportfile,'w')as f:
       f.write(html_code)

#html_codeToHTML("tmp/outfile.csv","report_file.html")
#    with open('report.html','w')as f:
#        f.write("".join(c))
