# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 16:30:22 2023

@author: Adam
"""

url = 'https://rpi.sodexomyway.com/dining-near-me/hours'

import urllib.request
import json

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

req = urllib.request.Request(url, headers=header)
page = urllib.request.urlopen(req)
page = page.read().decode("utf8")

test = page.split('<div class="dining-block">')

data = dict()

daystoletter = {'Monday': 'M', 'Tuesday': 'T', 'Wednesday': 'W', 'Thursday': 'R', 'Friday': 'F', 'Saturday': 'Sa', 'Sunday': 'Su'}
daystonumber = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 0}

rath = False
for i in range(1,len(test)):
    bldg = None 
    reghours = test[i].split('<h3>Regular Hours</h3>')[-1].split('arrayregdays')
    name = test[i].split('</a>')[0].split('>')[-1]
    name = name.replace('’',"'").replace('é','e')
    href = test[i].split('href="')[1].split('"')[0][16:]
    if " - " in name: bldg, name = name.split(" - ")
    if name == "The Commons Dining Hall": name = "Commons Dining Hall"
    print(name)

    if rath: bldg = "Student Union"
    if bldg:
        data.setdefault(bldg, {})
        data[bldg][name] = dict()
    else: data[name] = dict()

    # for day in daystoletter:
    #     #data[name][day] = dict()
    #     data[name][daystonumber[day]] = []
    
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
        hours = hours.split(' - ')
        
        for day in days:

            if len(hours) != 2: continue

            #data[name][daystonumber[day]].append([hours, note])

            start = convert_mil(hours[0])
            end = convert_mil(hours[1])
            if bldg: data[bldg][name]["{}:{}-{}:{}".format(daystonumber[day], start, daystonumber[day], end)] = note
            else:    data[name]["{}:{}-{}:{}".format(daystonumber[day], start, daystonumber[day], end)] = note

        daysstr = ''
        for day in days:
            daysstr += daystoletter[day]

    if bldg: data[bldg][name]["url"] = href
    else: data[name]["url"] = href

        # print("\t{}: {} {}".format(daysstr,hours, note))
    if '<h2>Student Union – Rathskeller</h2>' in test[i]: rath = True

with open('data/dining.json', 'w') as f:
    f.write(json.dumps(data, indent = 4))