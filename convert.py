from collections import defaultdict
from math import inf as inf
from datetime import date
from requests import get
import json
import sys
import os

SIS = access = printers = dining = None

roomsToSkip = [
  'Off-Campus',
  'Online',
  'TBA',
  ''
]

bldgsToSkip = [
  'Gurley Building',
  'Peoples Ave Complex J',
  'Nuclear Eng. And Sci. Bldg'
]

days = {
  'M': 1,
  'T': 2,
  'W': 3,
  'R': 4,
  'F': 5
}

corrections = {
  'Rcos == 1 Credit' : 'RCOS'
}

# Good enough for now
starting = {
  '1': 8,   # Spring
  '5': 20,  # Summer
  '8': 28,  # Fall
  '12': 21  # Winter
}

# Full list of buildings (incl. those w/o classes)
with open("data/info.json", 'r') as f: info = json.load(f)

abbrev = {v[0]: k for k, v in info.items()}

URL = "https://api.github.com/repos/quacs/quacs-data/contents/semester_data"

# Get the most recent courses.json from QuACS:
td = date.today(); day, month, year = td.day, td.month, td.year
data = get(URL).json()
if "message" in data:
  if "API rate limit exceeded" in data['message']:
    sys.exit("API rate limit exceeded!")
curSem = data[-1]['url']
# Pick current sem from what's already been recorded this year
for sem in reversed(data[-4:]):
  if int(sem['name'][:4]) == year: # Same year
      if starting.get(str(month)) and starting[str(month)] <= day: # Starts this month
        curSem = sem['url']
        break
      elif int(sem['name'][-2:]) < month: # Started month(s) ago
        curSem = sem['url']
        break

print(curSem)
content = get(curSem).json()
courses = get(content[1]['download_url']).json()

with open("courses.json", 'w') as f: json.dump(courses, f, indent=4)
with open("courses.json", 'r') as f: SIS = json.load(f)

# nested dicts; automatically create dicts when accessed
data = defaultdict(lambda: defaultdict(dict)) 

# courses.json is sorted by dept > course > sec > time block
# build data (to be data.json) sorted by building > room > class
byCRN = {}
titleToCRN = defaultdict(list)
for dept in SIS:
  for course in dept['courses']:
    numSecs = len(course['sections'])
    hasSecs = True if numSecs > 1 else False
    for sec in course['sections']:
      byCRN[sec['crn']] = sec['timeslots']
      titleToCRN[sec['title']].append(sec['crn']) 
      for block in sec['timeslots']:
        roomName = block['location'] # room name
        act, cap = sec['act'], sec['cap']
        size = act if act > cap else cap # class size estimate
        if size and roomName not in roomsToSkip and roomName[-1].isnumeric():
          for day in block['days']: # for every day its held, make new room instance:
            time = f"{days[day]}:{block['timeStart']:04}-{days[day]}:{block['timeEnd']:04}"
            title, secNum = sec['title'], sec['sec']
            if title in corrections: title = corrections[title]
            stats = [title, size, []]

            bldgName, roomNum = roomName.rsplit(' ', 1)
            if bldgName not in bldgsToSkip:
              room = data[abbrev[bldgName]][roomNum] # shorthand
              # key = room time; value = room stats
              if time not in room: room[time] = stats
              elif room[time][0] == title: # avoid test block overlap
                # sum of class sizes for concurrent time blocks
                room[time][1] += size
              # Adding sections... beware duplicates and crosslisted!
              if hasSecs and secNum not in room[time][2]: room[time][2].append(secNum) 

deptToCRN = {}
for dept in SIS:
  d = dept['code']
  deptToCRN[d] = {}
  for course in dept['courses']:
    c = course['crse']
    numSecs = len(course['sections'])
    deptToCRN[d][c] = {}
    for section in course['sections']:
      s = section['sec']
      deptToCRN[d][c][s] = section['crn']

with open("data/search/byCRN.json", 'w') as file: json.dump(byCRN, file, indent = 4)
# Class names to CRNs:   "Data Structures" -> [59979, ..., 62915]
with open("data/search/title_to_CRN.json", 'w') as file: json.dump(titleToCRN, file, indent = 4)
# Department codes to CRNs:   CSCI 1200 01 -> 59979
with open("data/search/dept_to_CRN.json", 'w') as f: json.dump(deptToCRN, f, indent=4) 

with open("data/access.json", 'r') as f: access = json.load(f)
with open("data/printers.json", 'r') as f: printers = json.load(f)
with open("data/dining.json", 'r') as f: dining = json.load(f)

# We've only added buildings with classes to data so far...
for name, details in info.items():
  if name not in data: data[name] = defaultdict(dict)

# sort rooms by their day and time
# meta: full names + hist page, room/building capacities, printers, & access times
for building, rooms in data.items():
  bldgMax = f = 0
  
  floors = []
  if building in access['numfloors']: floors.append(access['numfloors'][building])
  else: floors.append(access['numfloors']['default'])

  for room, times in rooms.items():
    data[building][room] = dict(sorted(times.items(), key=lambda x: x[0]))
    roomMax = 0
    for stats in data[building][room].values(): 
      if roomMax < stats[1]: roomMax = stats[1]
    data[building][room]['meta'] = { 'max': roomMax}
    bldgMax += roomMax
    if building in printers and room in printers[building]:
      data[building][room]['meta']['printers'] = printers[building][room]
  data[building]['meta'] = { 'max': bldgMax if bldgMax else None }
  if building not in access['times']:
    data[building]['meta']['access'] = access['times']['default']
  else: data[building]['meta']['access'] = access['times'][building]
  # Add name and history subdomain to meta
  data[building]['meta']['name'] = info[building][0]
  data[building]['meta']['hist'] = info[building][1]
  if building in access['entry']: floors.append(access['entry'][building])
  else: floors.append(access['entry']['default'])
  data[building]['meta']['floors'] = floors if floors[0] != inf else []
  if data[building]['meta']['name'] in dining:
      data[building]['meta']['dining'] = dining[data[building]['meta']['name']]

with open("data/data.json", 'w') as output: json.dump(data, output, indent = 4)
os.remove("courses.json") 