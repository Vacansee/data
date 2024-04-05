# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 16:23:13 2024

@author: Adam
"""
import requests
import json
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

import urllib.request
from selenium.webdriver.common.by import By

import time
from datetime import datetime


days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

all_buildings = "https://lp01.idea.rpi.edu/shiny/erickj4/StudySafeJSON/?list=TRUE"
url2 = 'https://lp01.idea.rpi.edu/shiny/erickj4/StudySafeJSON/?building=CII&day=Sunday&hour=12'

def get_url_data(building):
    url = "https://lp01.idea.rpi.edu/shiny/erickj4/StudySafeJSON/?building={}".format(building)
    return url

def get_json_from_url(url_input):

    '''
    Try to get this working with requests later,
    using selenium for now

    req = urllib.request.Request(url)
    page = urllib.request.urlopen(req)

    page = page.read().decode("utf8")

    soup = BeautifulSoup(page, 'html.parser')

    #For testing, use this to view scraped html
    with open('test.html', 'w', encoding = 'utf-8') as f:
        f.write(soup.prettify())

    r = requests.get(buildings_url, verify=False)
    soup = BeautifulSoup(r.content, 'html.parser')
    element = soup.find(id='hourly_crowd_json')
    print(element.text)
    '''

    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    UA = UserAgent().random # Create a random user agent
    options.add_argument(f'--user-agent={UA}')

    # Install appropriate webdriver for platform
    driver = webdriver.Chrome(options=options)

    driver.get(url_input)
    driver.implicitly_wait(10)
    time.sleep(2)

    pre_element = driver.find_element(By.ID, "hourly_crowd_json")
    #print(pre_element.text)
    json_data = json.loads(pre_element.text)    

    return json_data

def run_report():

    current_date = datetime.now().strftime('%Y-%m-%d')
    buildings = get_json_from_url(all_buildings)

    data = dict()

    for building in buildings:
        name = building['Building'].split(";")[-1]
        url = get_url_data(name)
        print(url)
        json_list = (get_json_from_url(url))
        #print(json)
        data[name] = json_list
    
    data = dict(data)
    print(type(data))

    with open("data/wifi/data_{}.json".format(current_date), 'w') as f:
        f.write(json.dumps(data, indent = 4))
