import json

with open("deptcodesectlist.json", 'r') as file: coursesdict = json.load(file)

def crnfromDepCodeSection(code, digit, section):
    return coursesdict[code][digit][section]