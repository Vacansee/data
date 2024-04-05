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

from datetime import datetime

url = 'https://cal.lib.rpi.edu/reserve/folsomlibrary/groupstudyrooms'

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

def add_block(hours):
    hour = int(hours[0:2])
    minutes = hours[2:4]
    
    assert(minutes == '00' or minutes == '15' or minutes=='30' or minutes == '45')
    
    if int(minutes) == 45:
        minutes = '00'
        hour = hour+1
    else:
        minutes = str(int(minutes)+15)
        
    if hour < 10:
        hour = "0{}".format(hour)
        
    if hour == 24:
        hour = '00'
        
    return "{}{}".format(hour, minutes)

        

def convert_mil(hours):
    times = hours.split(':')
    hour = int(times[0])
    minutes = times[1][0:2]
    
    if 'pm' in hours:
        hour += 12
    else:
        if hour < 10:
            hour = "0{}".format(hour)
    result = "{}{}".format(hour, minutes)
    return result

def get_bookings():
    
    today = datetime.today().weekday()
    day_number = (today + 1) % 7
    
    #req = urllib.request.Request(url, headers=header)
    #page = urllib.request.urlopen(req)
    #page = page.read().decode("utf8")
    
    data = dict()
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    UA = UserAgent().random # Create a random user agent
    options.add_argument(f'--user-agent={UA}')
    
    # Install appropriate webdriver for platform
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = webdriver.Chrome(options=options)

    
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
        data[room]["{}:{}-{}:{}".format(day_number, convert_mil(time), day_number, add_block(convert_mil(time)))] = [status, 0, []]
    
        
    with open('data/data.json', 'r') as file:
        roomsData = json.load(file)
        
    for room in rooms:
        print(room)
        roomsData['Folsom'][room] = data[room]
        
        # All study rooms but 353B have capacity 6, so hard code this
        if room == '353B':
            roomsData['Folsom'][room]['meta'] = {"max": 8}
        else:
            roomsData['Folsom'][room]['meta'] = {"max": 6}

        #print(data[room])
        
        
        
    # with open('data/library_data', 'w') as convert_file:
    #      convert_file.write(json.dumps(data))
         
    with open('data/data.json', 'w') as convert_file:
         convert_file.write(json.dumps(roomsData, indent = 4))
        
        
        
        
        
        
    
    
    
    
    
        
        
    