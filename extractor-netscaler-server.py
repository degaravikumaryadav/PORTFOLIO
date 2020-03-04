from lxml import html
import requests
import json
import time
import re
import logging
import asyncio
from timeit import default_timer
from concurrent.futures import ThreadPoolExecutor
import hertzcommons as hc

logging.basicConfig(level=logging.INFO, filename='netscalerHost.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def processNetscalerHost(data_source, source):
    data = json.loads(source)
    response = {}
    response[data_source['name']] = data['stats']['ns']
    return response

def main():
    config = {}
    config['source']={}
    # the base URL if we need to repeat
    config['source']['base_url'] =  'https://isd.hertz.com/ISDTools/ns/GetStats?ns='
    itemList = []
    # individual servers
    itemList.append({'name':'ns01dc','url':'ns01.dc.irac.ecom.ad.hertz.com'})
    itemList.append({'name':'ns01dc2','url':'ns01.dc2.irac.ecom.ad.hertz.com'})
    itemList.append({'name':'ns01rc','url':'ns01.rc.irac.ecom.ad.hertz.com'})
    config['source']["urls_to_fetch"] = itemList

    config["data_processor"] = processNetscalerHost
    config["splunk_source"] = "netscalerHostTest"
    config["time_interval"] = 30
    config["loop_count"] = -1
    hc.scrapeData(config)
     
main()
