#!/usr/bin/env python
# coding: utf-8

# # Webscrapping

# In[1]:


import json
import re
import os
from time import sleep
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


# In[2]:


mongodb_pass = json.load(open('API_Data.json'))['mongoDB_pass'] # password mongodb user
client = MongoClient(mongodb_pass)
db = client.nfl_data
mycoll = db.games


# ## Vorstellung des Website
# 
# Die Basis für die Spieldaten ist die offizielle Webseite der NFL *www.nfl.com*. Die Webseite  bietet ein Developer Portal mit einer API zum Abruf der Daten. Der Zugriff wird jedoch auf NFL Partner und Kunden beschränkt. {cite:p}`NFLdevportal`
# 
# Aufgrund des begrenzten Nutzerkreises erfolgt die Datenbeschaffung mit Webscrapping. Dies bedingt die Quelltext-Analyse. Die gescrappten Daten werden in die mongoDB-Datenbank geladen.
# 
# Für das Webscrapping werden verwendet:
# - Selenium im Chrome Browser
# - BeautifulSoup

# Unter *www.nfl.com/schedules* lassen sich die Spielergebnisse der letzten Spielwoche abrufen. Die folgende Abbildung zeigt ein DropDown-Menü über welches Kalenderjahre und zugehörige Wochen abgerufen werden können. .
# 
# ```{figure} /images/nfl_schedule.png
# ---
# name: nfl_schedule
# ---
# Screenshot NFL.com - Schedule Dropdown {cite:p}`NFLschedule`
# ```
# 
# Nach einem Klick auf diese Buttons verändert sich die URL nach einem bestimmten Schema. Dieses Verhalten wird genutzt, um die benötigten Links direkt anzusprechen. Für das Kalenderjahr 2021 und Woche 14 haben die Spielergebnisse folgende URL: *https://www.nfl.com/schedules/2021/REG14/*  
# Für reguläre Spielwochen besteht der Eintrag immer aus REG + Nummer der Woche. Für andere Events, wie beispielsweise den Superbowl, wird POST zzgl. Nummer verwendet.  
# Alternativ stellt die Selenium-Bibliothek Funktionen für Klicks zur Verfügung. Mit `find_element()` und `click()` können das Dropdown-Menü und die Cookie-Abfrage gesteuert werden, um die benötigte Website abzurufen. Jedoch handelt es sich bei den Abruf über das Linkschema, um die zielführende Variante.
# 
# Für das Scrapping wird in Vergangenheits- und Zukunftsdaten unterschieden. Die Vergangenheitsdaten werden mittels der beschriebenen Links abgerufen. Dazu wird nachfolgend eine Textdatei mit den benötigten Links erstellt.
# Das Scrappen der Zukunftsdaten verwendet einen leicht abgewandelten Code und wird im [Kapitel zur Cloud](gc_future) erläutert.

# In[ ]:


weeks = list()
years = ["2021","2022"]
for i in range(1,19):
    weeks.append("REG"+str(i))
    if i <= 4:
        weeks.append("POST"+str(i))
#path = "https://www.nfl.com/schedules/"+ year + "/" + week +"/"


# In[ ]:


urls = list()
for year in years:
    for week in weeks:
        urls.append("https://www.nfl.com/schedules/"+ year + "/" + week +"/")


# In[ ]:


with open('link_list.txt', 'w') as f:
    for line in urls:
        f.write(line)
        f.write('\n')


# ## Vorbereitung Scrapping
# 
# Beim Scrapping wird Chrome im Headless-Mode zusammen mit Selenium verwendet. Dazu wird nachfolgend eine Chrome-Instanz konfiguriert und aufgerufen.
# 
# Durch die Funktion `execute_script('return document.body.innerHTML')` wird der Webseiteninhalt geladen, auch wenn die Anzeige aus durch ein Cookie-Fenster blockiert wird. Dies ermöglicht ein Verzicht auf die oben beschriebene `find_element()` und `click()` Funktionen.  
# Im nächsten Schritt wird der Quelltext mit BeautifulSoup und lxml ausgelesen. Die Klasse `nfl-c-matchup-strip nfl-c-matchup-strip--post-game` beschreibt alle div-Container mit Spieldaten. D.h. pro Eintrag existiert ein div-Container mit dem `a-Tag` (html) = "aria-label". Diese Tag enthält Informationen über die spielenden Teams. Innerhalb des jeweiligen Containers befinden sich div-Container mit der class `nfl-c-matchup-strip__team-score`, welche die Spielergebnisse enthalten.

# In[3]:


#options.add_argument("--headless")
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


# In[4]:


example = webdriver.Chrome(executable_path="chromedriver",options=options)
example.get('https://www.nfl.com/schedules/2021/REG14/')
example_page = example.execute_script('return document.body.innerHTML')
example.quit()
soup_object = BeautifulSoup(''.join(example_page),'lxml')
div_list = soup_object.find_all('div', class_="nfl-c-matchup-strip nfl-c-matchup-strip--post-game")


# In[5]:


div_list[0]


# In[6]:


print(div_list[0].find()['aria-label'])
print('-'*20)
print(div_list[0].find_all('div',class_="nfl-c-matchup-strip__team-score"))
print('-'*20)
print('Score mit Index 0:',div_list[0].find_all('div',class_="nfl-c-matchup-strip__team-score")[0]['data-score'])
print('Score mit Index 1:',div_list[0].find_all('div',class_="nfl-c-matchup-strip__team-score")[1]['data-score'])


# Der obere Code-Block zeigt den Quelltext-Output für das Spiel *Vikings vs Steelers*. Nachfolgend ist ein Screenshot der Internetseite.  
# Auf der Internetseite werden die Teamnamen im Vergleich zum 'aria-label'-String verdreht, jedoch die Spielergebnisse in der Anzeigereihenfolge ausgelesen.
# 
# ```{figure} /images/nfl_schedule_vikingsVSsteelers.png
# ---
# name: nfl_schedule_vikings_steelers
# ---
# Screenshot NFL.com - Vikings vs Steelers {cite:p}`NFLschedule`
# ```
# 
# Diese Beobachtung ermöglicht das Speichern der Daten in strukturierter Form. Der String wird nach Leerzeichen gesplittet und der Split-Output mit Index abgerufen. Zum ersten Teamnamen wird der zweite Score-div-Container ausgelesen. Der folgende Codeblock enthält eine beispielhafte Darstellung zum Split der Teamnamen. Ferner wird die Logik gezeigt um Jahr und Woche des Spiels als Information zu ergänzen.

# In[7]:


print('Split-Ergebnis:',div_list[0].find()['aria-label'].split(' '))
print('-'*20)
print('Abruf nach Index:', div_list[0].find()['aria-label'].split(' ')[0])
print('Score mit Index 1:',div_list[0].find_all('div',class_="nfl-c-matchup-strip__team-score")[1]['data-score'])
print('-'*20)
myURL = 'https://www.nfl.com/schedules/2021/REG14/'
print('Jahr aus URL:',myURL.split('/')[-3])
print('Woche aus URL:','Week ' + re.sub(r'[^\d]+', '', myURL.split('/')[-2]))


# ## Scrapping
# Mit den oben beschriebenen Erkenntnissen werden Funktionen gebaut, welche das Scrappen mittels der Links aus einer Textdatei ermöglichen.
# 
# Zunächst wird eine URL aus der Textdatei ausgelesen und daraus gelöscht. Mit der jeweiligen URL wird die Internetseite abgerufen und ein BeautifulSoup-Objekt erzeugt. Auf dieses werden die beschriebenen Scrapping-Schritte durchgeführt.
# 
# Mit der pymongo-Funktion `insert_one()` werden die Daten in der Datenbank gespeichert. Das Scrapping wird nicht gestartet wenn die Datei link_list.txt leer ist. Vor und nach dem Ausführen der Website-Skripte wird 5 Sekunden gewartet um ein vollständiges Laden zu gewährleisten.

# In[ ]:


def get_current_week(should_delete = True):
    '''
    takes: optional input-parameter if url should be deleted, set to false for bugfixing
    returns: string from the file link_list.txt which is a url to nfl.com
    '''
    with open ('link_list.txt', 'r') as f:
        first_line = f.readline().split("\n")[0] #Lesen der ersten Zeile
        data = f.read().splitlines(True) #Lesen des gesamten Inhalts
    if should_delete:
        with open('link_list.txt', 'w') as f2:
            f2.writelines(data[0:])
    return first_line


# 
# ````{margin}
# ```{warning} Der Name der Washington Redskins wurde geändert. Für 2021 wurde deshalb der Name "Football Team" (zwei Wörter) verwendet, weshalb die String-Split-Logik nicht funktioniert. Durch eine Schleife wird der aktuelle Name "Commanders" verwendet, wenn als Teamname "Football" erkannt wird.
# ```
# ````

# In[ ]:


def get_page(myUrl):
    '''
    takes URL as string
    returns b4s-object
    '''
    driver = webdriver.Chrome(executable_path="chromedriver",options=options)
    driver.get(myUrl)
    sleep(5)
    page = driver.execute_script('return document.body.innerHTML')
    sleep(5)
    driver.quit()
    return BeautifulSoup(''.join(page),'lxml')

def get_teams_scores(mySoup):
    '''
    takes b4s-object output
    returns dictionary with teams and scores
    '''
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


# In[ ]:


'''
Actual Scrapping Run
'''
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

