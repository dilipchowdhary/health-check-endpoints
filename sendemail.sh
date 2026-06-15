(
echo "From: dvsuite.middleware.hcreports@verizon.com"
echo "To: murali.dontabhaktuni@verizon.com,VZW-VDSI-MCS.Middleware@verizon.com,VZW-VDSI-DVS-MCS.Middleware-Prod@verizon.com,sre.cicd.middleware@verizon.com"
echo "MIME-Version: 1.0"
echo "Subject: $1"
echo "Content-Type: text/html"
cat $2
) | sendmail -t -v
