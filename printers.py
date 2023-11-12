import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

URL = 'https://itssc.rpi.edu/hc/en-us/articles/360005151451-RCS-Public-Printers-Sorted-by-Location'

options = webdriver.ChromeOptions()
options.add_argument("--headless")
UA = UserAgent().random # Create a random user agent
options.add_argument(f'--user-agent={UA}')

# Install appropriate webdriver for platform
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.implicitly_wait(10)
driver.get(URL)

page = driver.page_source

start = page.find('<strong>Printer List</strong>')
end = page.find('Last Reviewed')

contents = page[start:end]
contents = contents.split('</tr>')

printers = dict()

rename = {
  'CII': 'Low',
  'Library': 'Folsom',
  'Student Union': 'Union',
  'East Campus Community Center': 'ECAV',
}

if page.find('<div class="l-padded-bottom captcha-container">') != -1 and len(contents) == 1:
    print("Captcha Error")

for i in range(1, len(contents)-1):
    # print(i)
    # print(contents[i])

    color = duplex = False

    printer_info = contents[i].split('</td>')

    building = printer_info[0].split('<td>')[-1]
    if building in rename:
        building = rename[building]
    building = building.replace(' ','_')

    room = printer_info[1].split('<td>')[-1]
    room = room.replace('<br>', ' ')

    if printer_info[3].split('<td>')[-1] != '&nbsp;':
        color = True

    printer_id = printer_info[2].split('<td>')[-1]

    paper_type = printer_info[4].split('<td>')[-1]
    paper_type = paper_type.replace('\u2033', '').replace('\u00d7', 'x').replace('<br>', ' ')
    
    if printer_info[5].split('<td>')[-1] != '&nbsp;':
        duplex = True

    dpi = printer_info[6].split('<td>')[-1]
    dpi = dpi.split()[0]
    
    if building not in printers:
        printers[building] = dict()

    if room not in printers[building]:
        #printers[building][room] = dict()
        printers[building][room] = []

    printers[building][room].append([printer_id, paper_type, dpi, color, duplex])

with open('printers.json', 'w') as convert_file:
     convert_file.write(json.dumps(printers))

driver.quit()