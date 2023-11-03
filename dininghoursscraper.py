# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 16:30:22 2023

@author: Adam
"""

#url = 'https://rpi.emscloudservice.com/web/BrowseEvents.aspx'
url = 'https://rpi.sodexomyway.com/dining-near-me/hours'

import urllib.request

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

data = []

for x in test:
    
    name = data[-1].split('</a>')[0].split('>')[-1]
    data.append(x.split('</div></div><div>')[0])
    
    times = data[-1].split('<p class="dining-block-hours">')
    
stop = 0    
for i in range(3):
    start = data[-1].find('<p data-arrayregdays', stop)
    stop = data[-1].find('</span><span>', start)
    print(start, stop)
    print(data[-1][start:stop])
    print()