from bs4 import BeautifulSoup
from  lxml import html
import pandas as pd
import requests
import json
import re
import time
import asyncio
from timeit import default_timer
from concurrent.futures import ThreadPoolExecutor
import hertzcommons as hc


i = 1
START_TIME = default_timer()


def processRateWSstats(source):
  soup = BeautifulSoup(source,'lxml')
  table = soup.find_all('table')[0] # Grab the first table

  totalRowCount = len(table.find_all('tr'))
  new_table = pd.DataFrame(columns=range(0,4),index=range(0,totalRowCount)) # I know the size 
  
  finalWS = {}
  row_marker = 0
  for row in table.find_all('tr'):
      column_marker = 0
      columns = row.find_all('td')
      if len(columns) > 2:
        tmp = hc.cleanAndStrip((columns[0].get_text()).strip() + (columns[1].get_text()).strip())
        finalWS[tmp] = hc.convertToFloat((columns[2].get_text()).strip())
        row_marker += 1
          
  return finalWS

def main():
    config = {}
    config["urls_to_fetch"] = [
        'https://ratesmonitor.hertz.com/RatesMonitoringWeb/rumPages/rumWebSLA.jsp?environment=prod'
    ]
    config["data_processor"] = processRateWSstats
    config["splunk_source"] = "rateWSTest"
    config["time_interval"] = 10
    config["loop_count"] = -1
    hc.scrapeData(config)
    
main()