import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
import os
from time import sleep

# MongoDB Access
mongodb_pass = json.load(open('API_Data.json'))['mongoDB_pass'] # password mongodb user
client = MongoClient(mongodb_pass)
db = client.gc_nfl
mycoll = db.gc_games

# Chrome Settings
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("lang=en")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--incognito")
options.add_argument("--disable-blink-features=AutomationControlled")


# Functions for Scrapping
def get_current_week(should_delete = True):
    with open ('link_list.txt', 'r') as f:
        first_line = f.readline().split("\n")[0] #Lesen der ersten Zeile
        data = f.read().splitlines(True) #Lesen des gesamten Inhalts
    if should_delete:
        with open('link_list.txt', 'w') as f2:
            f2.writelines(data[0:])
    print('red url from txt-file:',first_line)
    return first_line

def get_teams_scores(mySoup):
    teams = mySoup.find()['aria-label'].split(' ')
    # check for a game of the washington Football Team
    if teams[0] == 'Football':
        team1 = 'Commanders'
        team2 = teams[3]
    elif teams[2] == 'Football':
        team1 = teams[0]
        team2 = 'Commanders'
    else:
        team1 = teams[0]
        team2 = teams[2]

    s1 = mySoup.find_all('div',class_="nfl-c-matchup-strip__team-score")[1]['data-score']
    s2 = mySoup.find_all('div',class_="nfl-c-matchup-strip__team-score")[0]['data-score']
    return {'team1': team1, 'score1':s1, 'team2':team2, 'score2':s2}
    
def get_page(myUrl):
    driver = webdriver.Chrome(executable_path="chromedriver",options=options)
    driver.get(myUrl)
    print('pagetitle:',driver.title)
    sleep(5)
    page = driver.execute_script('return document.body.innerHTML')
    sleep(5)
    driver.quit()
    return BeautifulSoup(''.join(page),'lxml')

# Actual Scrapping Run
if os.stat('link_list.txt').st_size == 0:
    print('empty link list')
else:   
    url = get_current_week()
    soup = get_page(url)
    containers = soup.find_all('div', class_="nfl-c-matchup-strip nfl-c-matchup-strip--post-game")
    for i in containers:
        myDict = get_teams_scores(i)
        myDict['year'] = url.split('/')[-3]
        myDict['week'] = 'Week ' + re.sub(r'[^\d]+', '', url.split('/')[-2])
        mycoll.insert_one(myDict)
    print('succesful scrapping run')
