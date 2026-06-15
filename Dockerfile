FROM go0v-vzdocker.oneartifactoryprod.verizon.com/centos:centos7.9
USER root
ENV http_proxy http://proxy.ebiz.verizon.com:80 
ENV https_proxy http://proxy.ebiz.verizon.com:80 
ENV no_proxy 127.0.0.1,localhost,instance-data,169.254.169.254,.elb.amazonaws.com,.verizon.com,.ebiz.verizon.com,oneartifactory.verizon.com 
ENV URLLIST_FILE urlslist.txt
ENV REPORTFILE_HTML report/report_file_t1.html
RUN yum -y install epel-release
RUN yum -y install python3 python3-pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --user
COPY . .

CMD python3 main.py -f ${URLLIST_FILE} -r ${REPORTFILE_HTML}
