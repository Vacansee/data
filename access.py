from bs4 import BeautifulSoup as parse
from requests import get
import json

access = {}

skip = [
	"Heffner Alumni House",
	"Linac/NES",
	"Off Campus Commons",
	"Playhouse",
	"Student Transition Building",
	"Admissions Building",
	"1516 People\u2019s Ave",
	"41 9th Street",
	"Commons Dining Hall",
	"Bar-H Dining Hall",
	"Sage Dining Hall",
	"Blitman Dining",
]

rename = {
  "87 Gym": "'87 Gym",
  "Academy Hall": "Academy",
  "AS&RC": "Armory",
  "Greene Building": "Greene",
  "Carnegie Building": "Carnegie",
  "Pittsburgh Building": "Pittsburgh",
  "Sage Lab": "Sage",
  "Ricketts Building": "Ricketts",
  "Troy Building": "Troy",
  "J-Building": "J Complex",
  "Jonsson Engineering Center": "JEC",
  "Walker Lab": "Walker",
  "Science Center": "JROWL",
  "Folsom Library": "Folsom",
  "Student Union": "Union",
  "Cogswell Laboratory": "Cogswell",
  "West Hall": "West",
  "Biotech": "CBIS",
}

# url = "https://publicsafety.rpi.edu/campus-security/card-access-schedule"
# raw = get(url).content
# html = parse(raw, "html.parser")
# table = html.find_all("tbody")[0]

with open("test.html", "r") as raw:
	table = parse(raw, "html.parser")


for tr in table.find_all("tr"):
	building, _, times = [('?' if td.string == None else td.string) for td in tr.find_all("td")]

	if building not in skip:
		if building in rename: building = rename[building]
		if times == "24/7": times = "1-7: 0000-2400"
		access[building] = times

# print(access)
with open("access.json", "w") as output:
  json.dump(access, output)