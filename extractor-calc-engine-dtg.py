from bs4 import BeautifulSoup
from  lxml import html
import pandas as pd
import requests
import json
import re
import time
import logging
import asyncio
from timeit import default_timer
from concurrent.futures import ThreadPoolExecutor
import hertzcommons as hc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.INFO, filename='dtgCalcs.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


START_TIME = default_timer()

def extracRateCel(columns):
  rateEngineTotal = {}

  if len(columns) > 2:
    rateEngineTotal['total'] = hc.convertToFloat((columns[1].get_text()).strip())
    rateEngineTotal['app'] = hc.convertToFloat((columns[2].get_text()).strip())
    rateEngineTotal['db'] = hc.convertToFloat((columns[3].get_text()).strip())
    rateEngineTotal['gdd'] = hc.convertToFloat((columns[4].get_text()).strip())
    rateEngineTotal['rules'] = hc.convertToFloat((columns[5].get_text()).strip())
    rateEngineTotal['txn'] = hc.convertToFloat((columns[6].get_text()).strip())
    rateEngineTotal['tps'] = hc.convertToFloat((columns[7].get_text()).strip())

  return rateEngineTotal

def processCalcTable(cellTable):
  rows = cellTable.find_all('tr')
  return extracRateCel(rows[8].find_all('td'))

def processRateCalc(data_source, source):
  soup = BeautifulSoup(source,'lxml')
  cellTables = soup.find_all('table')
  #print('cell tables', len(cellTables))  
  #processSimple(cellTables[3])

  allEngines = {}
  allEngines['WASCell_01_DCDB6'] = processCalcTable(cellTables[2])
  allEngines['WASCell_02_DCDB7'] = processCalcTable(cellTables[4])
  allEngines['WASCell_03_DCDB8'] = processCalcTable(cellTables[6])
  allEngines['WASCell_04_DCDB9'] = processCalcTable(cellTables[8])
  allEngines['WASCell_05_DCDB10'] = processCalcTable(cellTables[10])
  allEngines['WASCell_06_DCDB11'] = processCalcTable(cellTables[12])

  allEngines['WASCell_01_RCDB6'] = processCalcTable(cellTables[3])
  allEngines['WASCell_02_RCDB7'] = processCalcTable(cellTables[5])
  allEngines['WASCell_03_RCDB8'] = processCalcTable(cellTables[7])
  allEngines['WASCell_04_RCDB9'] = processCalcTable(cellTables[9])
  allEngines['WASCell_05_RCDB10'] = processCalcTable(cellTables[11])
  allEngines['WASCell_06_RCDB11'] = processCalcTable(cellTables[13])

  return allEngines


def processSimple(table):
  for row in table.find_all('tr'):
    for cell in row.find_all('td'):
      print(cell.get_text(), end='  ')
    print()
  return

def main():
    config = {}
    config['source']={}
    # the base URL if we need to repeat
    config['source']['base_url'] =  'https://ratesmonitor.hertz.com/RatesMonitoringWeb/calculatorpages/calcdtgmonitoring.jsp?environment=prod'
    itemList = []
    # individual servers
    itemList.append({'name':'calcservers','url':''})
    config['source']["urls_to_fetch"] = itemList

    config["data_processor"] = processRateCalc
    config["splunk_source"] = "dtgCalcServers"
    config["time_interval"] = 30
    #set -1 for infinite loop
    config["loop_count"] = -1
    hc.scrapeData(config)
    
main()