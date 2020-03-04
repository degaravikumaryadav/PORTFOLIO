from  lxml import html
import requests
import json
import time
import re
import hertzcommons as hc


i = 1

def processSeamlessStats(source):
  lastSeamlessUpdate = {}
  # get throttle
  mysource = re.search("Throttle",source)
  seamlessThrottle = hc.cleanAndStrip((source[mysource.end()+4:mysource.end()+8]).strip())
  if seamlessThrottle == 'OFF':
    seamlessThrottle = 0
  else:
    seamlessThrottle = hc.convertToFloat(seamlessThrottle)
  lastSeamlessUpdate['throttle'] = seamlessThrottle
  myTPS = re.search("TIME=",source)
  lastSeamlessUpdate['updateTime'] = (source[myTPS.end():myTPS.end()+5]).strip()
  myTPS = re.search("TPS:",source)
  countStart=0
  countLength=8
  #lastSeamlessUpdate['counts'] = hc.convertToFloat((source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
  lastSeamlessUpdate['curTPS'] = float((source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
  countStart=17
  countLength=7
  #lastSeamlessUpdate['processTime'] = hc.convertToFloat((source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
  lastSeamlessUpdate['processTime'] = float((source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
  countStart=24
  countLength=11
  lastSeamlessUpdate['server'] = (source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip()
  myTPS = re.search("MQ TPS:",source)
  countStart=0
  countLength=8
  #lastSeamlessUpdate['mqTPS'] = hc.convertToFloat((source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
  lastSeamlessUpdate['mqTPS'] = float((source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
  myTPS = re.search("RAM ALL",source)
  countStart=0
  countLength=100
  ramText = (source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip()
  ramText = re.sub("<[^>]*>", "",ramText)
  ramText = re.sub("\s+", " ",ramText)
  ramParts = ramText.split(" ")
  #lastSeamlessUpdate['RAMALLavgTPS'] = hc.convertToFloat(ramParts[0])
  #lastSeamlessUpdate['RAMALLcurTime'] = hc.convertToFloat(ramParts[1])
  #lastSeamlessUpdate['RAMALLcurTPS'] = hc.convertToFloat(ramParts[2])
  #lastSeamlessUpdate['RAMALLcurTOperc'] = hc.convertToFloat(ramParts[3])
  #lastSeamlessUpdate['RAMALLcurTO'] = hc.convertToFloat(ramParts[4])
  lastSeamlessUpdate['RAMALLavgTPS'] = float(ramParts[0])
  lastSeamlessUpdate['RAMALLcurTime'] = float(ramParts[1])
  # When 23 or 24 are starting up after a reboot, fields are often blank.  If RAM ALL's CurTim, CurTPS, and CurTO% are blank, 
  # the first character found will be the '%' for CurTO%, which causes this line to error because it grabbed too much input.
  # The only way to fix this will be to use defined lengths with a start and end offset instead of grabbing 100 characters and 
  # parsing it all with a regex like it is currently.
  lastSeamlessUpdate['RAMALLcurTPS'] = float(ramParts[2])
  lastSeamlessUpdate['RAMALLcurTOperc'] = float(ramParts[3].replace('%',''))
  lastSeamlessUpdate['RAMALLcurTO'] = int(ramParts[4].replace(',',''))
  
  return lastSeamlessUpdate


url = 'https://http-inputs-intmonitor.splunkcloud.com:443/services/collector'
#body = {'source':"seamlessTest", 'event':'{"other":"mydata2", "test":"false", "maxconns":3235}'}
headers = {'Authorization': 'Splunk 0744481E-71F5-47CE-BBFC-192ABAE1898E'}



while i > 0 :
  page24 = requests.get('http://rclnpsmap24/cgi-bin/scmperf.ksh')
  lsu24 = processSeamlessStats(page24.text)
  body = {'source':"seamlessTest", 'event':lsu24}
  r = requests.post(url, data=json.dumps(body), headers=headers, verify=False)

  page23 = requests.get('http://dclnpsmap23/cgi-bin/scmperf.ksh')
  lsu23 = processSeamlessStats(page23.text)
  body = {'source':"seamlessTest", 'event':lsu23}
  r = requests.post(url, data=json.dumps(body), headers=headers, verify=False)

  print(lsu24)
  print(lsu23)
  # get TPS
  
  print("--")
  i+=1
  time.sleep(60)

