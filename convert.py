from collections import defaultdict
from datetime import date
from requests import get
import json

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

abbrev = {
  'Darrin Communications Center': 'DCC',
  'Academy Hall': 'Academy',
  'Low Center for Industrial Inn.': 'Low',
  'Voorhees Computing Center': 'VCC',
  'Alumni Sports and Rec Center': 'Armory',
  'Amos Eaton Hall': 'Amos_Eaton',
  'Greene Building': 'Greene',
  'Carnegie Building': 'Carnegie',
  'Pittsburgh Building': 'Pittsburgh',
  'Russell Sage Laboratory': 'Sage',
  'Ricketts Building': 'Ricketts',
  'Troy Building': 'Troy',
  'Lally Hall': 'Lally',
  'Jonsson Engineering Center': 'JEC',
  'Walker Laboratory': 'Walker',
  'Jonsson-Rowland Science Center': 'JROWL',
  'Folsom Library': 'Folsom',
  'Cogswell Laboratory': 'Cogswell',
  'West Hall': 'West',
  'Biotechnology and Interdis Bld': 'CBIS',
  'Materials Research Center': 'MRC'
}

expanded = {v: k for k, v in abbrev.items()}

URL = "https://api.github.com/repos/quacs/quacs-data/contents/semester_data"

# Get the most recent courses.json from QuACS:
month = date.today().month; year = date.today().year
data = get(URL).json()
curSem = data[-1]["url"]
# Pick current sem from what's already been recorded this year
for sem in reversed(data[-4:]):
  if int(sem['name'][:4]) == year:
    if int(sem['name'][-2:]) <= month: #TODO: precise sem cutoffs
      curSem = sem["url"]
      break

content = get(curSem).json()
courses = get(content[1]["download_url"]).json()

with open('courses.json', 'w') as file: json.dump(courses, file)
with open("courses.json", "r") as f: input = json.load(f)

# nested dicts; automatically create dicts when accessed
data = defaultdict(lambda: defaultdict(dict)) 

# courses.json is sorted by dept > course > sec > time block
# build data (to be rooms.json) sorted by building > room > class
for dept in input:
  for course in dept['courses']:
    for sec in course['sections']:
      for block in sec['timeslots']:
        roomName = block['location'] # room name
        act, cap = sec['act'], sec['cap']
        size = act if act > cap else cap # class size estimate
        if size and roomName not in roomsToSkip and roomName[-1].isnumeric():
          for day in block['days']: # for every day its held, make new room instance:
            time = f"{days[day]}:{block['timeStart']:04}-{days[day]}:{block['timeEnd']:04}"
            title = sec['title']
            if title in corrections: title = corrections[title]
            stats = [title, size]

            bldgName, roomNum = roomName.rsplit(' ', 1)
            if bldgName not in bldgsToSkip:
              room = data[abbrev[bldgName]][roomNum] # shorthand
              # key = room time; value = room stats
              if time not in room: room[time] = stats
              elif room[time][0] == title: # avoid test block overlap
                # sum of class sizes for concurrent time blocks
                room[time][1] += size

with open("access.json", "r") as f: access = json.load(f)
with open("printers.json", "r") as f: printers = json.load(f)

# sort rooms by their day and time
# meta: room/building capacities, printers, & access times
for building, rooms in data.items():
  bldgMax = 0
  for room, times in rooms.items():
    data[building][room] = dict(sorted(times.items(), key=lambda x: x[0]))
    roomMax = 0
    for stats in data[building][room].values(): 
      if roomMax < stats[1]: roomMax = stats[1]
    data[building][room]["meta"] = { "max": roomMax }
    bldgMax += roomMax
    if building in printers and room in printers[building]:
      data[building][room]["meta"]["printers"] = printers[building][room]
  data[building]["meta"] = { "max": bldgMax }
  if building not in access:
    data[building]["meta"]["access"] = access["default"]
  else: data[building]["meta"]["access"] = access[building]
  data[building]["meta"]["name"] = expanded[building]

with open("rooms.json", "w") as output: json.dump(data, output)