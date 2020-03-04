from lxml import html
import requests
import json
import time
import re
import logging
import asyncio
import sys, traceback
from timeit import default_timer
from concurrent.futures import ThreadPoolExecutor
import hertzcommons as hc

logging.basicConfig(level=logging.INFO, filename='seamless.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def processSeamlessStats(data_source, source):
    lastSeamlessUpdate = {}

    # get last section of the page
    lastSection = source.rfind("Throttle")
    if lastSection == 0:
        # couldn't find what we were looking for, return empty
        logging.warning('Process Seamless Data is empty')
        return
    try:
        source = source[lastSection:]
        mysource = re.search("Throttle", source)
        seamlessThrottle = hc.cleanAndStrip(
            (source[mysource.end()+4:mysource.end()+8]).strip())
        if seamlessThrottle == 'OFF':
            seamlessThrottle = 0
        else:
            seamlessThrottle = hc.convertToFloat(seamlessThrottle)
        lastSeamlessUpdate['throttle'] = seamlessThrottle
        myTPS = re.search("TIME=", source)
        lastSeamlessUpdate['updateTime'] = (
            source[myTPS.end():myTPS.end()+5]).strip()
        myTPS = re.search("TPS:", source)
        countStart = 0
        countLength = 8
        lastSeamlessUpdate['counts'] = hc.convertToFloat(
            (source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
        countStart = 17
        countLength = 7
        lastSeamlessUpdate['processTime'] = hc.convertToFloat(
            (source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
        countStart = 24
        countLength = 11
        lastSeamlessUpdate['server'] = (
            source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip()
        myTPS = re.search("MQ TPS:", source)
        countStart = 0
        countLength = 8
        lastSeamlessUpdate['mqTPS'] = hc.convertToFloat(
            (source[myTPS.end()+countStart:myTPS.end()+(countStart+countLength)]).strip())
        myTPS = re.search("RAM ALL", source)
        countStart = 0
        countLength = 100
        ramText = (source[myTPS.end()+countStart:myTPS.end() +
                        (countStart+countLength)]).strip()
        ramText = re.sub("<[^>]*>", "", ramText)
        ramText = re.sub("\s+", " ", ramText)
        ramParts = ramText.split(" ")
        
        # handle seamless errors
        if len(ramParts) > 4:
            lastSeamlessUpdate['RAMALLavgTPS'] = hc.convertToFloat(ramParts[0])
            lastSeamlessUpdate['RAMALLcurTime'] = hc.convertToFloat(ramParts[1])
            lastSeamlessUpdate['RAMALLcurTPS'] = hc.convertToFloat(ramParts[2])
            lastSeamlessUpdate['RAMALLcurTOperc'] = hc.cleanNumbers(ramParts[3])
            lastSeamlessUpdate['RAMALLcurTO'] = hc.cleanNumbers(ramParts[4])

        serverData = {}
        serverData[data_source['name']] = lastSeamlessUpdate
    except:
        logging.warning("error processing seamless data")
        traceback.print_exc(file=sys.stdout)
        return
    print(serverData)
    return serverData

def main():
    config = {}
    config['source']={}
    # the base URL if we need to repeat
    config['source']['base_url'] =  ''
    itemList = []
    # individual servers
    itemList.append({'name':'smap24','url':'http://rclnpsmap24/cgi-bin/scmperf.ksh'})
    itemList.append({'name':'smap23','url':'http://dclnpsmap23/cgi-bin/scmperf.ksh'})
    config['source']["urls_to_fetch"] = itemList

    config["data_processor"] = processSeamlessStats
    config["splunk_source"] = "seamlessTest"
    config["time_interval"] = 30
    config["loop_count"] = -1
    hc.scrapeData(config)
     
main()