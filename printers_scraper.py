import requests

import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import platform
from selenium.webdriver.chrome.service import Service

import json

url = 'https://itssc.rpi.edu/hc/en-us/articles/360005151451-RCS-Public-Printers-Sorted-by-Location'

# a = requests.get(url)
# print(a.text)

# header= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
#       'AppleWebKit/537.11 (KHTML, like Gecko) '
#       'Chrome/23.0.1271.64 Safari/537.11',
#       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
#       'Accept-Encoding': 'none',
#       'Accept-Language': 'en-US,en;q=0.8',
#       'Connection': 'keep-alive'}

# req = urllib.request.Request(url, headers=header)

# fp = urllib.request.urlopen(url)
# mybytes = fp.read()

# mystr = mybytes.decode("utf8")
# fp.close()

# print(mystr)

#Method 2: Use selenium

options = webdriver.ChromeOptions()
#options.add_argument("--headless")

#This is the default path on linux, but probably isn't neccacary tbh
service = Service(executable_path = r'/usr/bin/chromedriver')
if platform.system() == 'Windows':
    driver = webdriver.Chrome(options=options)
else:
    driver = webdriver.Chrome(service = service, options=options)

driver.implicitly_wait(10)
driver.get(url)

mystr = driver.page_source

start = mystr.find('<strong>Printer List</strong>')
end = mystr.find('Last Reviewed')

contents = mystr[start:end]
contents = contents.split('</tr>')

printerdict = dict()

for i in range(1, len(contents)-1):
    print(i)
    print(contents[i])
    
    color = False
    duplex = False
    
    printer_info = contents[i].split('</td>')
    building = printer_info[0].split('<td>')[-1]
    room = printer_info[1].split('<td>')[-1]
    if printer_info[3].split('<td>')[-1] != '&nbsp;':
        color = True
    printer_id = printer_info[2].split('<td>')[-1]
    paper_type = printer_info[4].split('<td>')[-1]
    if printer_info[5].split('<td>')[-1] != '&nbsp;':
        duplex = True
    dpi = printer_info[6].split('<td>')[-1]
    
    
    if building not in printerdict:
        printerdict[building] = dict()
        
    if room not in printerdict[building]:
        printerdict[building][room] = dict()
        
    printerdict[building][room][printer_id] = dict()
    
    printerdict[building][room][printer_id]['paper_type'] = paper_type
    printerdict[building][room][printer_id]['dpi'] = dpi
    printerdict[building][room][printer_id]['color'] = color
    printerdict[building][room][printer_id]['duplex'] = duplex

    
with open('newprinters.json', 'w') as convert_file:
     convert_file.write(json.dumps(printerdict, indent=4))

driver.quit()