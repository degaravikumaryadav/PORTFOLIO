from  lxml import html
import requests
import json
import time


i = 1

while i < 6 :
  page = requests.get('https://isd.hertz.com/ISDTools/ns/GetStats?ns=ns01.rc.irac.ecom.ad.hertz.com')
  data = page.json()
  mySystem = data['stats']['ns']

  print(mySystem['tcpcurclientconn'])
  i+=1
  time.sleep(5)

#print(data['stats']['severity'])

#tree = html.fromstring(page.content)
#This will create a list of buyers:
#buyers = tree.xpath('//div[@title="buyer-name"]/text()')
#This will create a list of prices
#prices = tree.xpath('//span[@class="item-price"]/text()')

#print 'Buyers: ', buyers
#print 'Prices: ', prices