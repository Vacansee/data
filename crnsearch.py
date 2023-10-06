import json

with open("crnlist.json", 'r') as f:
    crndata = json.load(f)

with open("crntotitle.json", 'r') as f:
    titles = json.load(f)
    
flag = True
while(flag):
    crn = input("Enter CRN:")
    dataDict = crndata[crn][0]
    title = titles[crn]

    print("Course Title: " + title)
    print("Instructor: " + dataDict['instructor'])
    print(title + " runs " + dataDict['dateStart'] + " to " + dataDict['dateEnd'])
    print(title + " meets on " + str(dataDict['days']) + " from " + str(dataDict['timeStart']) + " to " + str(dataDict['timeEnd']))
    print(title + " is held at " + dataDict['location'])
    print()

    resFlag = False
    while(resFlag == False):
        askAgain = input("Search another course? (Y or N)")
        if(askAgain == 'Y' or askAgain == 'y'):
            print("----------------------------------------")
            resFlag = True
        elif(askAgain == 'N' or askAgain == 'n'):
            print("Thank you for using CRN Search Shell")
            resFlag = True
            flag = False

