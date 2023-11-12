from collections import defaultdict
from math import inf as inf
from datetime import date
from requests import get
import json
import sys

input = access = printers = None

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

# Full list of buildings (incl. those w/o classes)
with open("info.json", 'r') as f: info = json.load(f)

abbrev = {v[0]: k for k, v in info.items()}

URL = "https://api.github.com/repos/quacs/quacs-data/contents/semester_data"

# Get the most recent courses.json from QuACS:
month = date.today().month; year = date.today().year
data = get(URL).json()
if "message" in data:
  if "API rate limit exceeded" in data['message']:
    sys.exit("API rate limit exceeded!")
curSem = data[-1]['url']
# Pick current sem from what's already been recorded this year
for sem in reversed(data[-4:]):
  if int(sem['name'][:4]) == year:
    if int(sem['name'][-2:]) <= month: #TODO: precise sem cutoffs
      curSem = sem['url']
      break
print(curSem)
content = get(curSem).json()
courses = get(content[1]['download_url']).json()

with open("courses.json", 'w') as file: json.dump(courses, file, indent=4)
with open("courses.json", 'r') as f: input = json.load(f)

# nested dicts; automatically create dicts when accessed
data = defaultdict(lambda: defaultdict(dict)) 

# courses.json is sorted by dept > course > sec > time block
# build data (to be rooms.json) sorted by building > room > class

#crnlist.json:
#{CRN: [{Building: .., Time:.., RoomNum:..},{Building: .., Time:.., RoomNum:..}]}
crnlist = {}
crnToTitleList = {}
for dept in input:
  for course in dept['courses']:
    numSecs = len(course['sections'])
    hasSecs = True if numSecs > 1 else False
    for sec in course['sections']:
      crnlist[sec['crn']] = sec['timeslots']
      crnToTitleList[sec['crn']] = sec['title']
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

with open("crnlist.json", 'w') as file: json.dump(crnlist, file, indent = 4)
with open("crntotitle.json", 'w') as file: json.dump(crnToTitleList, file, indent = 4)

with open("access.json", 'r') as f: access = json.load(f)
with open("printers.json", 'r') as f: printers = json.load(f)

#{CRN: [{Building: .., Time:.., RoomNum:..},{Building: .., Time:.., RoomNum:..}]}
deptcodesectlist = {}
for dept in input:
  deptcode = dept['code']
  deptcodesectlist[deptcode] = {}
  for course in dept['courses']:
    coursecode = course['crse']
    numSecs = len(course['sections'])
    deptcodesectlist[deptcode][coursecode] = {}
    for section in course['sections']:
      sectioncode = section['sec']
      crn = section['crn']
      deptcodesectlist[deptcode][coursecode][sectioncode] = crn

with open("deptcodesectlist.json", 'w') as file: json.dump(deptcodesectlist, file, indent=4)

# We've only added buildings with classes to data so far...
for name, details in info.items():
  if name not in data: data[name] = defaultdict(dict)

# sort rooms by their day and time
# meta: full names + hist page, room/building capacities, printers, & access times
for building, rooms in data.items():
  bldgMax = f = 0
  floors = [inf, -inf]
  for room, times in rooms.items():
    if room[0].isdecimal():
      f = int(room[0]) # room "[3]08"
      if f < floors[0]: floors[0] = f
      if f > floors[1]: floors[1] = f
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

with open("rooms.json", 'w') as output: json.dump(data, output, indent = 4)