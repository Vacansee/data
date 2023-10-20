from selenium import webdriver
import platform
from selenium.webdriver.chrome.service import Service

import json
import time
from fake_useragent import UserAgent


url = 'https://itssc.rpi.edu/hc/en-us/articles/360005151451-RCS-Public-Printers-Sorted-by-Location'

options = webdriver.ChromeOptions()
options.add_argument("--headless")

ua = UserAgent()
user_agent = ua.random
options.add_argument(f'--user-agent={user_agent}')


# Note: Running this program running requires downloading the most recent chromedriver version
# If on Windows, Visit https://chromedriver.chromium.org/downloads to download, put in same directory as this program
# On linux, use sudo apt-get install chromium-chromedriver
# Not sure about mac, but probably a similar approach to windows

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

if mystr.find('<div class="l-padded-bottom captcha-container">') != -1 and len(contents) == 1:
    print("Captcha Error")

for i in range(1, len(contents)-1):
    print(i)
    print(contents[i])
    
    color = False
    duplex = False
    
    printer_info = contents[i].split('</td>')
    
    building = printer_info[0].split('<td>')[-1]
    building.replace(' ','_')
    
    room = printer_info[1].split('<td>')[-1]
    room = room.replace('<br>', ' ')
    
    if printer_info[3].split('<td>')[-1] != '&nbsp;':
        color = True
        
    printer_id = printer_info[2].split('<td>')[-1]
    
    paper_type = printer_info[4].split('<td>')[-1]
    paper_type = paper_type.replace('\u2033', '')
    paper_type = paper_type.replace('\u00d7', 'x')
    paper_type = paper_type.replace('<br>', ' ')
    
    if printer_info[5].split('<td>')[-1] != '&nbsp;':
        duplex = True
        
    dpi = printer_info[6].split('<td>')[-1]
    dpi = dpi.split()[0]
    
    if building not in printerdict:
        printerdict[building] = dict()
        
    if room not in printerdict[building]:
        #printerdict[building][room] = dict()
        printerdict[building][room] = []
        
    #printerdict[building][room][printer_id] = dict()
    printerdict[building][room].append([printer_id, paper_type, dpi, color, duplex])
    
    # printerdict[building][room][printer_id]['paper_type'] = paper_type
    # printerdict[building][room][printer_id]['dpi'] = dpi
    # printerdict[building][room][printer_id]['color'] = color
    # printerdict[building][room][printer_id]['duplex'] = duplex
    
with open('newprinters.json', 'w') as convert_file:
     convert_file.write(json.dumps(printerdict)

driver.quit()