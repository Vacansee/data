# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 16:30:22 2023

@author: Adam
"""

url = 'https://rpi.sodexomyway.com/dining-near-me/hours'

import urllib.request
import json
from bs4 import BeautifulSoup

# no spaces, replace non standard chars, use numbers as index from days
#   starting with sunday = 0

def convert_mil(hours):
    if hours[-2:] == 'PM':
        times = hours[:-2].split(':')
        hour = int(times[0])
        minutes = times[1]
        hour += 12
        result = "{}:{}".format(hour, minutes)
    else:
        times = hours[:-2].split(':')
        hour = int(times[0])
        minutes = times[1]
        if hour < 10:
            hour = "0{}".format(hour)
        result = "{}:{}".format(hour, minutes)
    return result 

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

rename = {

}

def write_json():

    req = urllib.request.Request(url, headers=header)
    page = urllib.request.urlopen(req)
    page = page.read().decode("utf8")
    
    data = dict()
    
    daystoletter = {'Monday': 'M', 'Tuesday': 'T', 'Wednesday': 'W', 'Thursday': 'R', 'Friday': 'F', 'Saturday': 'Sa', 'Sunday': 'Su'}
    daystonumber = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 0}
    
    soup = BeautifulSoup(page, 'html.parser')
    
    # For testing, use this to view scraped html
    # with open('test.html', 'w') as f:
    #     f.write(soup.prettify())
        
    results = soup.find("ul", {"style" : "list-style-type:none;"})
    
    locations = results.findAll("div", {"class" : "dining-block"})
    
    for location in locations:
        name = location.find('a').string
        name = name.replace('’',"'").replace('é','e').split(" - ")[-1]
        if name == "The Commons Dining Hall": name = "Commons Dining Hall"
    
        print(name)
        data[name] = dict()
        
        regtime = location.find("div", {"class" : "reghours"})
        regdays = regtime.findAll("dt", {"class" : "dining-block-days"})
        #reghours = regtime.findAll("span", {"class" : "dining-block-hours"})
        info = regtime.findAll("dd")
        
        for i in range(len(regdays)):
            regday = regdays[i]['data-arrayregdays'].split(',')
            #reghour = reghours[i].string
            
            reghour2 = info[i].find("span", {"class" : "dining-block-hours"}).string
            
            note_elem = info[i].findAll("span", {"class": "dining-block-note"})
            if len(note_elem) == 0:
                note = note = ''
            else:
                note = note_elem[0].string.strip(':')
                
            print(reghour2)
            if reghour2 == 'Closed':
                continue
                            
            reghour2 = reghour2.split(' - ')
            
            start = convert_mil(reghour2[0])
            end = convert_mil(reghour2[1])
    
            for day in regday:
                
                print("\t{}:{}-{}:{} {}".format(daystonumber[day], start, daystonumber[day], end, note))
    
                data[name]["{}:{}-{}:{}".format(daystonumber[day], start, daystonumber[day], end)] = note
    
    with open('data/dining.json', 'w') as f:
        f.write(json.dumps(data, indent = 4))
        
write_json()