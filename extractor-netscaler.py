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

logging.basicConfig(level=logging.INFO, filename='netscaler.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def processNetscaler(data_source, source):
    # get the stats for these endpoint in the Netscaler
    netscalerList = ['vssl_XML_2007a_Lookup', 'vssl_XML_2007a_Other','vssl_XML_2004a', 'vssl_XML_General', ]
    data = json.loads(source)
    response = {}
    response[data_source['name']] = {}
    # get just the nodes we are interested in
    for nsServer in data["lbvserver"]:
        if nsServer["name"] in netscalerList :
            response[data_source['name']][nsServer["name"]] = nsServer 

    #print(response)
    return response

def main():
    config = {}
    config['source']={}
    # the base URL if we need to repeat
    config['source']['base_url'] =  'https://isd.hertz.com/ISDTools/ns/GetStats?ns='
    itemList = []
    # individual servers
    itemList.append({'name':'ns01dc','url':'ns01.dc.irac.ecom.ad.hertz.com&detail=lbvservers'})
    itemList.append({'name':'ns01dc2','url':'ns01.dc2.irac.ecom.ad.hertz.com&detail=lbvservers'})
    itemList.append({'name':'ns01rc','url':'ns01.rc.irac.ecom.ad.hertz.com&detail=lbvservers'})
    config['source']["urls_to_fetch"] = itemList

    config["data_processor"] = processNetscaler
    config["splunk_source"] = "netscalerTest"
    config["time_interval"] = 20
    config["loop_count"] = -1
    hc.scrapeData(config)
     
main()
