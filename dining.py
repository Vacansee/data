# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 16:30:22 2023

@author: Adam
"""

import urllib.request
import json
from bs4 import BeautifulSoup

# no spaces, replace non standard chars, use numbers as index from days
#   starting with sunday = 0

header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
  "AppleWebKit/537.11 (KHTML, like Gecko) "
  "Chrome/23.0.1271.64 Safari/537.11",
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
  "Accept-Encoding": "none",
  "Accept-Language": "en-US,en;q=0.8",
  "Connection": "keep-alive",
}

rename = {}
exclude = ["Have A Nice Day!"]
existing_meal_names = ["Brunch", "Dinner", "Lunch", "Breakfast"]

def convert_mil(hours):
  if hours[-2:] == "PM":
    times = hours[:-2].split(":")
    hour = int(times[0])
    minutes = times[1]
    hour += 12
    result = "{}:{}".format(hour, minutes)
  else:
    times = hours[:-2].split(":")
    hour = int(times[0])
    minutes = times[1]
    if hour < 10:
      hour = "0{}".format(hour)
    result = "{}:{}".format(hour, minutes)
  return result

def get_hours():
  url = "https://rpi.sodexomyway.com/dining-near-me/hours"

  req = urllib.request.Request(url, headers=header)
  page = urllib.request.urlopen(req)
  page = page.read().decode("utf8")

  data = dict()
  data['Student Union'] = dict()
  data['DCC'] = dict()
  data['Sage'] = dict()
  data['Folsom'] = dict()

  daystoletter = {
    "Monday": "M",
    "Tuesday": "T",
    "Wednesday": "W",
    "Thursday": "R",
    "Friday": "F",
    "Saturday": "Sa",
    "Sunday": "Su",
  }
  days_to_num = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 0}

  soup = BeautifulSoup(page, "html.parser")

  # For testing, use this to view scraped html
  # with open('test.html', 'w') as f:
  #      f.write(soup.prettify())

  results = soup.find("ul", {"style": "list-style-type:none;"})
  
  headers = results.findAll("li", {"class": "dining-group"})
  
  for dining_header in headers:
      headerName = dining_header.find("h2").text
      #print(headerName)
      
      locations = dining_header.findAll("div", {"class": "dining-block"})
    
      for location in locations:
        
        rath = False
        
        name = location.find("a").string
        print(name)
        
        #print("HEADER NAME:", headerName.split(" – ")[0])
        if name.split(" - ")[0] == "Student Union" or headerName.find("Student Union") != -1:
            print("{} --- RATH IS TRUE".format(name))
            rath = True
        
        
        #if name.find()
        
        name = name.replace("’", "'").replace("é", "e").split(" - ")[-1]
        url = location.find("a")["href"]
        url = "/".join(url.split('/')[2:])
        
        if name == "The Commons Dining Hall":
          name = "Commons Dining Hall"
            
        if rath:
            data["Student Union"][name] = dict()
        elif name == "The Beanery Cafe":
            data['Sage'][name] = dict()
        elif name == "DCC Cafe":
            data['DCC'][name] = dict()
        elif name == "Argo Tea":
            data['Folsom'][name] = dict()
        else:
            data[name] = dict()
    
        regtime = location.find("div", {"class": "reghours"})
        regdays = regtime.findAll("dt", {"class": "dining-block-days"})
        info = regtime.findAll("dd")
            
        for i in range(len(regdays)):
          regday = regdays[i]["data-arrayregdays"].split(",")
          reghour2 = info[i].find("span", {"class": "dining-block-hours"}).string
    
          note_elem = info[i].findAll("span", {"class": "dining-block-note"})
          if len(note_elem) == 0:
            note = note = ""
          else:
            note = note_elem[0].string.strip(":")
    
          if reghour2 == "Closed": continue
          reghour2 = reghour2.split(" - ")
    
          start = convert_mil(reghour2[0])
          end = convert_mil(reghour2[1])
    
          for day in regday:
            print("\t{}:{}-{}:{} {}".format(days_to_num[day], start, days_to_num[day], end, note))
            if rath:
                data['Student Union'][name]["{}:{}-{}:{}".format(days_to_num[day], start, days_to_num[day], end)] = note
            elif name == "The Beanery Cafe":
                data['Sage'][name]["{}:{}-{}:{}".format(days_to_num[day], start, days_to_num[day], end)] = note
            elif name == "DCC Cafe":
                data['DCC'][name]["{}:{}-{}:{}".format(days_to_num[day], start, days_to_num[day], end)] = note
            elif name == "Argo Tea":
                data['Folsom'][name]["{}:{}-{}:{}".format(days_to_num[day], start, days_to_num[day], end)] = note
            else:
                data[name]["{}:{}-{}:{}".format(days_to_num[day], start, days_to_num[day], end)] = note
                
        if rath:
            data["Student Union"][name]["url"] = url
        elif name == "The Beanery Cafe":
            data['Sage'][name]["url"] = url
        elif name == "DCC Cafe":
            data['DCC'][name]["url"] = url
        elif name == "Argo Tea":
            data['Folsom'][name]["url"] = url
        else:
            data[name]["url"] = url


  with open("data/dining.json", "w") as f:
    f.write(json.dumps(data, indent=4))

"""
  Commons: https://menus.sodexomyway.com/BiteMenu/Menu?menuId=15465&locationId=76929001&whereami=http://rpi.sodexomyway.com/dining-near-me/commons-dining-hall
  Russell sage: https://menus.sodexomyway.com/BiteMenu/Menu?menuId=15285&locationId=76929002&whereami=http://rpi.sodexomyway.com/dining-near-me/commons-dining-hall
  BARH: https://menus.sodexomyway.com/BiteMenu/Menu?menuId=15286&locationId=76929003&whereami=http://rpi.sodexomyway.com/dining-near-me/commons-dining-hall
  Blitman: https://menus.sodexomyway.com/BiteMenu/Menu?menuId=15288&locationId=76929015&whereami=http://rpi.sodexomyway.com/dining-near-me/commons-dining-hall
"""

def get_menu_options():
  urls = {
    "Commons": "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=15465&locationId=76929001&whereami=http://rpi.sodexomyway.com/dining-near-me/commons-dining-hall",
    "Russell Sage": "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=15285&locationId=76929002&whereami=http://rpi.sodexomyway.com/dining-near-me/commons-dining-hall",
    "BARH": "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=15286&locationId=76929003&whereami=http://rpi.sodexomyway.com/dining-near-me/commons-dining-hall",
    "Blitman": "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=15288&locationId=76929015&whereami=http://rpi.sodexomyway.com/dining-near-me/commons-dining-hall",
  }
  data = dict()

  for dining_hall in urls:

    url = urls[dining_hall]

    req = urllib.request.Request(url, headers=header)
    page = urllib.request.urlopen(req)
    page = page.read().decode("utf8")

    soup = BeautifulSoup(page, "html.parser")

    # For testing, use this to view scraped html
    with open("test.html", "w", encoding="utf-8") as f:
      f.write(soup.prettify())

    print("================================\n\n\n")
    print("DONE WITH REQUEST!!")

    # To find day:
    # <div class="bite-day-menu" id="menuid-30-day">, where day = day of month

    # Under a day, there are multiple blocks
    # <div class="accordion-block brunch">

    # List of menu items in <ul aria-describedby="course-ff03fb20b5" class="bite-menu-item">

    # Gets all 7 days of the current week
    menu_day = soup.findAll("div", {"class": "bite-day-menu"})

    # menu_day = menu_day[0:1] Only get first day

    data[dining_hall] = dict()

    for day in menu_day:
      day_num = day.attrs["id"].split("-")[1]
      data[dining_hall][day_num] = dict()
      print(day_num)
      # day = menu_day[0] #only for testing
      meals = day.findAll("div", {"class": "accordion-block"})

      for meal in meals:
        # meal = meals[0] #only for testing
        meal_name = meal.attrs["class"][-1].title()
        data[dining_hall][day_num][meal_name] = dict()
        print(meal_name)

        if meal_name not in existing_meal_names:
          print("Parsing error! Check meal name")
          assert True == False  # delete this later

        courses = meal.findAll("div", {"class": "bite-menu-course"})
        menus = meal.findAll("ul", {"class": "bite-menu-item"})

        # Courses represents the name of the station (eg, bakery)
        # Menus is the list of menu offerings for that station, and is not
        # nested, so we have to search both and loop through them together.
        # Therefore each menu corresponds to a course (station) so the num should be equal
        assert len(courses) == len(menus)

        for i in range(len(courses)):
          course_name = courses[i].find("h5").text.title()
          data[dining_hall][day_num][meal_name][course_name] = dict()
          print("\t\t", courses[i].find("h5").text)
          menu_items = menus[i].findAll("li")

          for item in menu_items:
            info = item.findAll("a")
            item_name = info[0].text

            if item_name in exclude: continue

            data[dining_hall][day_num][meal_name][course_name][item_name] = []
            print("\t\t\t", item_name)

            for j in range(1, len(info)):
              data[dining_hall][day_num][meal_name][course_name][info[0].text].append(info[j].text)

            allergens = item.findAll("img")
            for allg in allergens:
              data[dining_hall][day_num][meal_name][course_name][info[0].text].append(allg.attrs["alt"])

    with open("data/menus.json", "w") as f:
      f.write(json.dumps(data, indent=4))

#get_menu_options()
get_hours()
