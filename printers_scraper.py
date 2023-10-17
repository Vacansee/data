import requests

import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import platform
from selenium.webdriver.chrome.service import Service

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

for i in range(1, len(contents)):
    print(contents[i])
    printer_info = contents[i].split('</td>')
    building = printer_info[0].split('<td>')[-1]
    room = printer_info[1].split('<td>')[-1]
    printer_id = printer_info[2].split('<td>')[-1]
    paper_type = printer_info[4].split('<td>')[-1]
    dpi = printer_info[6].split('<td>')[-1]
    
    
    
    
    

driver.quit()