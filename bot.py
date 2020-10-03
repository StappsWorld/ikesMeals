from lxml import html
from sys import exit
from datetime import datetime
from os import path, makedirs
import json
import requests


def validate(date_text):
    try:
        return datetime.strptime(date_text, '%m-%d-%Y').strftime('%m-%d-%Y')
    except ValueError:
        raise ValueError("Incorrect data format, should be MM-DD-YYYY")


def getMealHash(specifiedDate, saving):
    """A function to request the mealplan for a specific date for Ike's Dining Hall at George Mason University

    This function uses Sodexo's website's API to generate a Hashmap of the mealplan of a specified date.

    Args:
        specifiedDate (str): the date the user is requesting
        saving (boolean): boolean value to pass if file read/write efficiency should be used

    Returns:
        Dict: the mealplan for that day in {MealTime(str) : {Station(str) : [ Meal Items(str) ]}} format
    """

    validate(specifiedDate)

    # Contacting the API to get meals on specified day
    url = f"https://menus.sodexomyway.com/BiteMenu/MenuOnly?menuId=16653&locationId=27747017&whereami=http://masondining.sodexomyway.com/dining-near-me/ikes&startDate={specifiedDate}"

    folderPath = "./json"
    filePath = f"{folderPath}/{specifiedDate}.json"

    if path.exists(filePath) and saving:
        jsonToParse = json.load(open(filePath, "r"))
    else:
        page = requests.get(url)
        tree = html.fromstring(page.content)

        jsonUnparsedTag = tree.xpath("//*[@id='nutData']")[0]

        if jsonUnparsedTag is not None:
            jsonUnparsed = jsonUnparsedTag.text

            jsonToParse = json.loads(jsonUnparsed)

            if saving:
                if not path.exists(folderPath):
                    makedirs(folderPath)
                open(filePath, "x")

                json.dump(jsonToParse, open(filePath, "w"))
        else:
            raise Exception(
                f"There was an error contacting the API, please try later or try a different date ({specifiedDate})")

    # Get the meal data for this specific day from it's day of the week (their api returns the whole week -_-)
    jsonParsed = jsonToParse[int(datetime.strptime(
        specifiedDate, '%m-%d-%Y').strftime('%w'))].get('dayParts')

    meals = {}

    # Their API is really disorganized, it has lists and hashmaps everywhere, kinda annoying... Iterating through each
    for dayPart in jsonParsed:
        for part in dayPart['courses']:
            if part['courseName'] == "-" or part['courseName'] is None:
                continue

            menuItems = part['menuItems']

            for item in menuItems:

                # Getting the components of each item that we want:
                meal = item["meal"]
                course = item["course"]
                formalName = item["formalName"]

                if course is None or course == "None" or course == "-" or course == "null":
                    continue

                # Logic to create custom hashmaps for each station and its items
                try:
                    currentMeal = meals[meal]
                    try:
                        currentCourse = currentMeal[course]
                        meals[meal][course].append(formalName)
                    except:
                        meals[meal].update({course: [formalName]})
                except:
                    meals.update({meal: {course: [formalName]}})
    return meals


def main():
    dateInput = input("What day would you like? (MM-DD-YYYY, or today) ")

    if dateInput.lower() == "today":
        specifiedDate = datetime.today().strftime('%m-%d-%Y')
    else:
        specifiedDate = validate(dateInput)

    meals = getMealHash(specifiedDate, True)

    for time in meals:
        print(f"For {time}: ")
        stations = meals.get(time)
        for station in stations:
            print(f"    at {station} we have: ")
            mealNames = stations.get(station)
            for mealName in mealNames:
                print(f"        -{mealName}")
        print()


if __name__ == "__main__":
    main()
