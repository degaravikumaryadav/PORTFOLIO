import requests
import json
import re
import time
import logging
import asyncio
import sys, traceback, urllib3, certifi
from timeit import default_timer
from concurrent.futures import ThreadPoolExecutor

START_TIME = default_timer()
logging.captureWarnings(True)

# DEV 
# splunk_url = 'https://http-inputs-intmonitor.splunkcloud.com:443/services/collector'
#headers = {'Authorization': 'Splunk 0744481E-71F5-47CE-BBFC-192ABAE1898E'}
#verifySSL = False

# Prod
splunk_url = 'https://http-inputs-intmonitor.splunkcloud.com:443/services/collector'
headers = {'Authorization': 'Splunk 0744481E-71F5-47CE-BBFC-192ABAE1898E'}
verifySSL = True

def cleanAndStrip(text):
  return re.sub("\W", "",text)

def convertToFloat(text):
  result = 0.0 
  try:
    result = float((text))
  except:
    logging.warning('could not process text to float %s', text)  
  return result

def cleanNumbers(text):
  result = 0.0 
  try:
    result = float(re.sub('[^0-9.]','', text))
  except:
    logging.warning('could not process clean text to float %s',text)  
  return result

###########  Splunk Functions 
def sendToSplunk(config, data_source, postData):
  if postData is None:
      logging.warning('no data returned from processer')
      return
  try:
    splunkDataSource= config["splunk_source"]
    body = {'source': splunkDataSource, 'event': postData}
    return requests.post(splunk_url, data=json.dumps(body), headers=headers, verify=verifySSL)
  except:
    logging.warning("Could not send data to splunk")
    traceback.print_exc(file=sys.stdout)
  return

def fetch(session, data_source, config):
  # we have a complex object for URL
  url = config['source']['base_url']+data_source['url']
  START_TIME = default_timer()
  with session.get(url) as response:
      if response.status_code != 200:
          logging.error("FAILURE::{0}".format(url))      
      try:
        timeLapse = default_timer() - START_TIME
        logging.info('Retrieved File: %s  [%.3f s]',url,timeLapse)
        processedData = config["data_processor"](data_source, response.text)  
        # only send if we have data
        if processedData is None:
          logging.warning("Empty Data to Splunk")
        else:
          sendToSplunk(config, data_source, processedData)      
      except:
        logging.warning('Problem procssing data in call')
        traceback.print_exc(file=sys.stdout)
      return 

async def get_data_asynchronous(config):
  with ThreadPoolExecutor(max_workers=10) as executor:
      with requests.Session() as session:
          # Set any session parameters here before calling `fetch`
          loop = asyncio.get_event_loop()
          tasks = [
              loop.run_in_executor(
                  executor,
                  fetch,
                  # Allows us to pass in multiple arguments to `fetch`
                  *(session, data_source, config)
              )
              for data_source in config['source']['urls_to_fetch']
          ]
          for response in await asyncio.gather(*tasks):
            pass

def scrapeData(config):
  keepLooping = True
  i = 0
  loop = asyncio.get_event_loop()
  while keepLooping:
    try:
      future = asyncio.ensure_future(get_data_asynchronous(config))
      loop.run_until_complete(future)
    except:
      logging.warning('Problem making threaded calls')
      traceback.print_exc(file=sys.stdout)
    # Run indefinitely if set to -1
    i += 1
    if (config["loop_count"] > 0) and (i == config["loop_count"]):
        keepLooping = False
    print('..',i )
    time.sleep(config["time_interval"])