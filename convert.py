from collections import defaultdict
from requests import get
import json

input = None

roomsToSkip = [
  'Off-Campus',
  'Online',
  'TBA',
  ''
]

days = {
  'M': 1,
  'T': 2,
  'W': 3,
  'R': 4,
  'F': 5
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
  'Gurley Building': 'Gurley',
  'Peoples Ave Complex J': 'J Complex',
  'Jonsson Engineering Center': 'JEC',
  'Walker Laboratory': 'Walker',
  'Jonsson-Rowland Science Center': 'JROWL',
  'Folsom Library': 'Folsom',
  'Cogswell Laboratory': 'Cogswell',
  'West Hall': 'West',
  'Nuclear Eng. And Sci. Bldg': 'NES',
  'Biotechnology and Interdis Bld': 'CBIS',
  'Materials Research Center': 'MRC'
}

URL = "https://api.github.com/repos/quacs/quacs-data/contents/semester_data"

data = get(URL).json()
recent = data[-1]["url"]
content = get(recent).json()

courses = get(content[1]["download_url"]).json()

with open('courses.json', 'w') as file:
    json.dump(courses, file)


with open("courses.json", "r") as f:
  input = json.load(f)
  # print(input)

data = defaultdict(lambda: defaultdict(dict)) 

for dept in input:
  for course in dept['courses']:
    for sec in course['sections']:
      for block in sec['timeslots']:
        r_name = block['location']
        act, cap = sec['act'], sec['cap']
        size = act if act > cap else cap
        if size and r_name not in roomsToSkip and r_name[-1].isnumeric():
          for day in block['days']:
            # time = (days[day], block['timeStart'], block['timeEnd'])
            time = f"{days[day]}: {block['timeStart']:04}-{block['timeEnd']:04}"
            stats = [sec['title'], size]

            b_name, r_num = r_name.rsplit(' ', 1)

            room = data[abbrev[b_name]][r_num]
            if time not in room:
              room[time] = stats
            else: room[time][-1] += stats[-1]


for building, rooms in data.items():
  for room, times in rooms.items():
    data[building][room] = dict(sorted(times.items(), key=lambda x: x[0]))

with open("rooms.json", "w") as output:
  json.dump(data, output)