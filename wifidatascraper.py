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


days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

url = "https://lp01.idea.rpi.edu/shiny/erickj4/StudySafeJSON/?building={}&day={}&hour={}"
buildings_url = "https://lp01.idea.rpi.edu/shiny/erickj4/StudySafeJSON/?list=TRUE"
url2 = 'https://lp01.idea.rpi.edu/shiny/erickj4/StudySafeJSON/?building=CII&day=Sunday&hour=12'

def get_all_buildings():
    
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

    
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    UA = UserAgent().random # Create a random user agent
    options.add_argument(f'--user-agent={UA}')
    
    # Install appropriate webdriver for platform
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.implicitly_wait(10)
    driver.get(buildings_url)
    
    pre_element = driver.find_element(By.ID, "hourly_crowd_json")
    pre_element.text
    
    page = driver.page_source


