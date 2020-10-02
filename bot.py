from selenium import webdriver
from bs4 import BeautifulSoup
from sys import exit
from datetime import datetime
import json

def validate(date_text):
    try:
        return datetime.strptime(date_text, '%m-%d-%Y').strftime('%m-%d-%Y')
    except ValueError:
        raise ValueError("Incorrect data format, should be MM-DD-YYYY")

dateInput = input("What day would you like? (MM-DD-YYYY, or today) ")



if dateInput.lower() == "today":
    specifiedDate = datetime.today().strftime('%m-%d-%Y')
else:
    specifiedDate = validate(dateInput)


# Contacting the API to get meals on specified day
url = f"https://menus.sodexomyway.com/BiteMenu/MenuOnly?menuId=16653&locationId=27747017&whereami=http://masondining.sodexomyway.com/dining-near-me/ikes&startDate={specifiedDate}"
#print(url)

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options)

driver.get(url)

jsonUnparsedTag = driver.find_element_by_xpath("/html/body/div/div[11]")

#print(jsonUnparsedTag)

if jsonUnparsedTag is not None:
    jsonUnparsed = jsonUnparsedTag.text

    #print(datetime.strptime(specifiedDate, '%m-%d-%Y').strftime('%w'))

    #Get the meal data for this specific day from it's day of the week (their api returns the whole week -_-)
    jsonParsed = json.loads(jsonUnparsed)[int(datetime.strptime(specifiedDate, '%m-%d-%Y').strftime('%w'))].get('dayParts')

    #print(jsonParsed)

    meals = {}

    #Their API is really disorganized, it has lists and hashmaps everywhere, kinda annoying... Iterating through each
    for dayPart in jsonParsed:
        for part in dayPart['courses']:
            if part['courseName'] == "-" or part['courseName'] is None:
                pass
            
            menuItems = part['menuItems']

            for item in menuItems:
                
                #Getting the components of each item that we want:
                meal = item["meal"]
                course = item["course"]
                formalName = item["formalName"]

                if course is None:
                    pass

                #Logic to create custom hashmaps for each station and its items
                stationAndName = {}
                try:
                    currentMeal = meals[meal]
                    try:
                        currentCourse = currentMeal[course]
                        meals[meal][course].append(formalName)
                    except:
                        meals[meal].update({course : [formalName]})
                except:
                    meals.update({meal : {course: [formalName]}})
    
    for time in meals:
        print(f"For {time}: ")
        stations = meals.get(time)
        for station in stations:
            print(f"    at {station} we have: ")
            mealNames = stations.get(station)
            for mealName in mealNames:
                print(f"        -{mealName}")
        print()

    #print(jsonParsed)
else:
    print(f"There was an error contacting the API, please try later or try a different date ({specifiedDate})")





###Attempted to webscrape, found the API...
###
###button = driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/div[2]/div[1]/a[1]")
###
###button.click()
###
###
###body = driver.page_source
###
###soup = BeautifulSoup(body, "lxml")
###
###
####Getting meal data to be parsed
###accordion = []
###
###meals = {"breakfast", "lunch", "dinner"}
###
###for meal in meals:
###    accordion.append(soup.find('div', attrs={"class" : f"accordion-block {meal}"}))
###
####Parsing meal data
###
###items = {}
###
###for meal in accordion:
###    listOfStations = meal.findAll('div', attrs={"class": "bite-menu-course"})
###    listOfItems = meal.findAll('ul', attrs={"class": "bite-menu-item"})
###
###    listOfStationNames = []
###    for station in listOfStations:
###        listOfStationNames.append(station.find("h5").string)
###
###    stationItems = []
###    for items in listOfItems:
###        listOfSubItems = items.findAll("li")
###        listOfItemNames = []
###        for item in listOfSubItems:
###            listOfItemNames.append(items.find("div", attrs={"class", "col-xs-9"}).find("a").text)
###        stationItems.append(listOfItemNames)
###
###    print(stationItems)
###
###
###
###
###