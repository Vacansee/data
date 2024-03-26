# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 16:58:43 2024

@author: Adam
"""

#Requests imports
import urllib.request
import json
from bs4 import BeautifulSoup

#Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

url = 'https://cal.lib.rpi.edu/reserve/folsomlibrary/groupstudyrooms'

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

def convert_mil(hours):
    times = hours.split(':')
    hour = int(times[0])
    minutes = times[1][0:2]
    
    if 'pm' in hours:
        hour += 12
    else:
        if hour < 10:
            hour = "0{}".format(hour)
    result = "{}:{}".format(hour, minutes)
    return result

def get_bookings():
    
    #req = urllib.request.Request(url, headers=header)
    #page = urllib.request.urlopen(req)
    #page = page.read().decode("utf8")
    
    data = dict()
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    UA = UserAgent().random # Create a random user agent
    options.add_argument(f'--user-agent={UA}')
    
    # Install appropriate webdriver for platform
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.implicitly_wait(10)
    driver.get(url)
    
    page = driver.page_source
    
    soup = BeautifulSoup(page, 'html.parser')
    
    driver.close()
        
    #For testing, use this to view scraped html
    with open('test.html', 'w', encoding = 'utf-8') as f:
        f.write(soup.prettify())
        
    rooms = soup.findAll("span", {"class": "fc-datagrid-cell-main"})
    
    table = soup.findAll("table", {"class": "fc-scrollgrid-sync-table table-bordered"})
    assert(len(table) == 1)
    table = table[0]
    
    slots = table.findAll("div", {"class": "fc-timeline-event-harness"})
    
    rooms = set()
    
    for slot in slots:
        
        description = slot.find("a").attrs['title']
        description = description.split('-')
        
        time = description[0].strip()
        room = description[1].strip()
        status = description[2].strip()
        
        if room not in rooms:
            rooms.add(room)
        
        print(time, room, status)
        
        if room not in data:
            data[room] = dict()
        data[room][convert_mil(time)] = status
        
    with open('data/data.json', 'r') as file:
        roomsData = json.load(file)
        
    roomsData['Folsom']
        
    with open('data/library_data', 'w') as convert_file:
         convert_file.write(json.dumps(data))
        
        
        
        
        
        
    
    
    
    
    
        
        
    