import requests
import json

#url = 'https://input-prd-p-zq5c6j4pkb5p.cloud.splunk.com:8088/services/collector'
url = 'https://http-inputs-intmonitor.splunkcloud.com:443/services/collector'
body = {'source':"seamlessTest", 'event':'{"other":"mydata2", "test":"false", "maxconns":3235}'}
#headers = {'Authorization': 'Splunk c6d14a9e-1561-4f82-98ff-c5d9a3a2acc7'}
headers = {'Authorization': 'Splunk 0744481E-71F5-47CE-BBFC-192ABAE1898E'}

r = requests.post(url, data=json.dumps(body), headers=headers, verify=False)

