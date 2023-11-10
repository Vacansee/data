# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 16:30:22 2023

@author: Adam
"""

url = 'https://rpi.sodexomyway.com/dining-near-me/hours'

import urllib.request
import json

header= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

req = urllib.request.Request(url, headers=header)
page = urllib.request.urlopen(req)
page = page.read()
mystr = page.decode("utf8")

test = mystr.split('<div class="dining-block">')

data = dict()

daystoletter = {'Monday': 'M', 'Tuesday': 'T', 'Wednesday': 'W', 'Thursday': 'R', 'Friday': 'F', 'Saturday': 'Sa', 'Sunday': 'Su'}

for i in range(1,len(test)):
    name = test[i].split('</a>')[0].split('>')[-1]
    reghours = test[i].split('<h3>Regular Hours</h3>')[-1].split('arrayregdays')
    
    print(name)
    
    data[name] = dict()
    for day in daystoletter:
        #data[name][day] = dict()
        data[name][day] = []
    
    specmessage = False
    if test[i].find('<div class="spechours hide">') != -1:
        specmessage = True
        special_message = test[i].split('<div class="spechours hide"><div><h3>')
        
    for j in range(1, len(reghours)):
        note = ''
        if reghours[j].find('<p class="dining-block-note">') != -1:
            note = reghours[j].split('<p class="dining-block-note">')[-1].split('</p>')[0]
            note = note.strip(' :-"')
        days = reghours[j].split('class=')[0].strip('"= ').split(',')
        hours = reghours[j].split('<p class="dining-block-hours">')[-1].split('</p>')[0]
        
        for day in days:
            data[name][day].append([hours, note])
        
        daysstr = ''
        for day in days:
            daysstr += daystoletter[day]
        
        print("\t{}: {} {}".format(daysstr,hours, note))
        
with open('dining_hours.json', 'w') as convert_file:
     convert_file.write(json.dumps(data, indent = 4))