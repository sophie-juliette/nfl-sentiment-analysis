#!/usr/bin/env python
# coding: utf-8

# (gc_analysis)=
# # Datenaufbereitung

# In diesem Notebook werden die Daten aus Webscrapping und der Sentimentanalyse für die Analyse vorbereitetet und angereichert. 

# In[1]:


import json
import pandas as pd
import numpy as np 
from pymongo import MongoClient
from scipy.stats import ttest_ind
from difflib import SequenceMatcher

#import plotly.express as px
#import plotly.figure_factory as ff
#from plotly.offline import init_notebook_mode
#init_notebook_mode() # To show plotly plots when notebook is exported to html


# In[2]:


mongodb_pass = json.load(open('API_Data.json'))['mongoDB_pass'] # password mongodb user
client = MongoClient(mongodb_pass)
db = client.gc_nfl
mycoll = db.gc_games


# 
# ````{margin}
# ```{note} Da die Youtube-Kommentare sehr lang sein können, wird die maximale Zeichenlänge der Zellen im Dataframe erhöht.
# ```
# ````

# In[3]:


pd.options.display.max_colwidth = 1000


# ## Hole Daten von MongoDB

# Dafür werden zu nächste die Daten aus mongodb abgerufen und in einen Dataframe umgewandelt. Die explorative Datenanalyse wird am Beispiel der Season 2021/2022 gezeigt, da diese Season bereits abgeschlossen ist.

# In[4]:


pipeline = [
        {'$match':{'year':'2021'}},
        {'$project':{
                '_id':0
        }}
        ]

x = mycoll.aggregate(pipeline)


# In[5]:


df0 = pd.DataFrame.from_dict(x)


# ## Vorbereitung Entitäten

# Für den Erkenntnisgewinn sind die Enitäten der Kommentare interessant, welche Mannschaftsnamen enthalten. Die Mannschaftsnamen der NFL-Teams bestehen aus zwei Bestandteilen: einen Namen des Heimatsort (z.B. Tampa Bay) und einem Teamnamen (z.B. Buccaneers). Ziel der Data Preperation ist es so viele Enitäten, wie möglich als Mannschaftsnamen zu identifizieren. Dafür müssen Synonyme wie z.B. Spitznamen oder nur der Heimatort als Mannschaftsnamen und Rechtschreibfehler erkannt werden. 

# In[6]:


df0.head(5)


# ### Berücksichtigung von Rechtschreibungsfehler

# Insofern die Entitäten mit Rechtschreibfehler von Google NLP erkannt wurden, sollen diese mit Hilfe des SequenceMatchers und Casefold zu einem "team_by_entity"-Wert zugeordnet werden.

# In[7]:


df0['entity'] = df0['entity'].apply(lambda x: x.casefold())


# Der SequenceMatcher berechent einen Ähnlichkeitswert von zwei Strings. Für das Projekt wird der Grenzwert auf 0.8 festgelegt. Mit der Funktion `match_sequence()` können die Teamnamen mit den Enität aus den Kommentaren abgeglichen werden. Liegt Ähnlichkeit vor, werden die Teamnamen der Enitäten korrigiert. 

# In[37]:


myStr1 = "Titans"
myStr2 = "tittans"

SequenceMatcher(a=myStr1.casefold(),b=myStr2.casefold()).ratio()


# In[8]:


def match_sequence(string1, string2):
    '''
    Input: string1 -> Entität
           string2 -> Textstelle im Kommentar
    '''
    value = string2
    if (SequenceMatcher(a = string1.casefold(), b = string2.casefold()).ratio() > 0.8):
        value = string1
    return value


# In[9]:


df0['entity']= df0.apply(lambda x: match_sequence(x['team1'], x['entity']), axis=1)
df0['entity']= df0.apply(lambda x: match_sequence(x['team2'], x['entity']), axis=1)


# Mit der Anwendung des SequenceMatcher konnten 965 weitere Enitäten zugeordnet werden. 

# ### Erstellungen eines Synonym-Wörterbuchs 

# Die Datenbasis des Synonym-Wörterbuchs ist eine Tabelle aus Github, welche die vollständigen Mannschaftsnamen enthält. 

# In[10]:


nfl_teams = pd.read_csv('https://gist.githubusercontent.com/cnizzardini/13d0a072adb35a0d5817/raw/f315c97c7677845668a9c26e9093d0d550533b00/nfl_teams.csv')
nfl_teams['Name_1'] = nfl_teams['Name'].apply(lambda x : x.split()[-1])
nfl_teams['Name_2'] = nfl_teams['Name'].apply(lambda x : " ".join(x.split()[0:-1]))


# In[11]:


nfl_teams.head()


# Mit den Spalten 'Name_1' und 'Name_2' wird der vollständige Mannschaftsname in den Teamname und den Heimatort getrennt, um die ersten Synonyme zu erhalten. Der Teamname dient in den nachfolgenden Betrachtungen als zentrale Entität ("team_by_entity") für den Mannschaftsnamen. Alle anderen Synonyme werden dem Teamnamen zugeordnetet. 
# 
# Nachfolgend wird die Tabelle mit den gebildeten Entitäten verschlankt. Die Werte für "team_by_entity" werden mit dem zugehörigen Synonymen kombiniert und unterhalb der bestehenden Tabelle angefügt. Schließlich werden die Spaltennamen umbenannt.

# In[12]:


df_name2 = nfl_teams[['Name_1','Name_2']].copy(deep=True)
df_name1 = nfl_teams[['Name_1']].copy(deep=True)
df_name1['Name'] = df_name1['Name_1']


# In[13]:


nfl_teams = nfl_teams.merge(df_name2.rename(columns={'Name_2':'Name'}),how='outer')
nfl_teams = nfl_teams.merge(df_name1,how='outer')
nfl_teams.drop(['ID','Abbreviation', 'Conference','Division','Name_2'], axis=1, inplace=True)
nfl_teams.rename(columns={'Name':'entity','Name_1':'team_by_entity'}, inplace=True)


# In[14]:


vikings = nfl_teams[nfl_teams['team_by_entity'] == "Packers"] 
vikings


# Für die Mannschaft "Packers" ist "Cheeseheads" ein sehr gängiger Spitzname. Solche Entitäten sollen ebenfalls berücksichtigt werden. Mit der nachfolgenden Funktion können derartige Synonyme hinzugeügt werden. Exemplarisch wird dies für drei Teams durchgeführt. 

# In[15]:


def append_pairs(df, entity, team_by_entity, single=True):
    '''
    takes: pandas dataframe, entity and team_by_entity, trigger for multiple or single values
    if single=False the input for entity and team_by_entity has to be a list.
    returns a pandas dataframe object that includes old and new data.
    '''
    if single:
        new_pair = {
                    'entity':[entity],
                    'team_by_entity':[team_by_entity]
                }
    else:
        new_pair = {
                    'entity':entity,
                    'team_by_entity':team_by_entity
                }   
    return pd.concat([df,pd.DataFrame(new_pair)])


# In[16]:


nfl_teams = append_pairs(nfl_teams, "Cheeseheads", "Packers", single=True)
nfl_teams = append_pairs(nfl_teams, "Redskins", "Commanders", single=True)
nfl_teams = append_pairs(nfl_teams, "Bucs", "Buccaneers", single=True)


# Es ist denkbar, die Synonyme noch deutlich weiter zu ergänzen, z.B. mit den Namen der Quaterbacks. Dem Team "Buccaneers" könnte so weitere 1700 Kommentare mit der Entität "Brady" zugeordnet werden. 

# ### Anwendung des Synonym-Wörterbuchs

# Das Synonym-Wörterbuch wird im folgenden auf den gesamten Dataframe angewendet.

# In[17]:


df0['entity'] = df0['entity'].apply(lambda x: x.casefold())


# In[18]:


df0['team_by_entity'] = None
for index, row in nfl_teams.iterrows():
    df0['team_by_entity'] = np.where(df0['entity'] == row['entity'].casefold(),row['team_by_entity'], df0['team_by_entity'])


# In[19]:


df0['team_by_entity'].unique()


# In[20]:


df0['team_by_entity'].isna().sum()


# Die Dokumente, welche keiner "team_by_enity" zugeordnet werden konnten, werden entfernt. 

# In[21]:


df0.dropna(subset='team_by_entity').head()


# Ebenfalls werden die Dokumente entfernt, welche ein Teamnamen enthalten, welcher nicht für das betrachtete Spiel relevant ist und damit nicht die Stimmung der spielenden Mannschaften repräsentieren, z.B. ein Kommentar zu den Cowboys im Spiel der Packers gegen Buccaners.

# ## Anreichung des DataFrames

# In[23]:


df0['team_by_entity'] = np.where((df0['team_by_entity'] == df0['team1']) | (df0['team_by_entity'] == df0['team2']), df0['team_by_entity'], None )


# Im nächsten Schritt werden den Größen 'Score' und 'Magnitude' ein "Sentiment" zugeordnet. Dafür werden Schwellenwerte für negativ, neutral und positiv festgelegt. 
# 
# |senitment|score|magnitude|
# |---------|-----|------|
# |positive| > 0.1| > 0.1|
# |negative| > -0.1| >0.1|
# |neutral| <= abs(0.1) | <= 0.1|

# Um an dieser Stelle den "Floating-point error" zu umgehen, werden die Fließkommazahlen mit 10 multipliziert und in einen Integer umgewandelt, sodass sie ohne Fehler verglichen werden können. 

# In[24]:


df0['sentiment'] = "" 
series_score = (df0['score']*10).astype(int)
series_mag = (df0['magnitude']*10).astype(int)
df0['sentiment'] = np.where((abs(series_score) <= 1) & (series_mag <= 1), 'neutral', df0['sentiment'] )
df0['sentiment'] = np.where((series_score <= -1) & (series_mag > 1), 'negative', df0['sentiment'] )
df0['sentiment'] = np.where((series_score >= 1) & (series_mag  > 1), 'positive', df0['sentiment'] )
df0.head(3)


# Für die Analyse werden zwei weitere Spalten erzeugt. Die Spalte "win_for_entity" enthält die Attribute "win", "draw" oder "defeat", je nachdem ob die Entität aus der Zeile gewonnen oder verloren hat. 
# Die Spalte "winner" enthält jeweils die Mannschaft, welche gewonnen hat. 

# In[25]:


df0['score1'] = df0['score1'].astype('int')
df0['score2'] = df0['score2'].astype('int')
df0['win_for_entity'] = 'draw'
df0['winner'] = np.where(df0['score1']>df0['score2'],df0['team1'],df0['team2'])
df0['win_for_entity'] = np.where(df0['winner']==df0['team_by_entity'],'win','defeat')
df0.head(3)


# ## Aggregation 

# Die bisherige Bearbeitung dient als Grundlage, um für die Analyse ein Tabelle mit Kennzahlen pro Mannschaft und Spiel zu bilden. 

# Die aggregierte Analyse-Tabelle soll folgenden Aufbau haben: 
# 
# * Mannschaft
# * Spielwoche
# * Ausgang: Sieg/Niederlage/Unentschieden 
# * Durchschnittlicher Sentiment Score
# * Anzahl Kommentare mit positiven Sentiment
# * Anzahl Kommentare mit negativen Sentiment
# * Anzahl Kommentare mit neutralen Sentiment

# Zum Zählen der Sentimentwerte wurde einen Funktion geschrieben, um Fehler zu vermeiden falls eine Kategorie (positive, negative, neutral) nicht vorkommt. 

# In[26]:


def count_sentiment(inp_series, sentiment_value): 
    try: 
        count = inp_series.value_counts()[sentiment_value]
    except: 
        count = 0
    return count


# Die Aggragtion erfolgt über die Spalten "team_by_entity" und "week" mit den Funktionen: 
# * first, zum Bestimmen des Ausgangs 
# * mean, zur Bildung des durchschnittlichen Sentiment Scores
# * count_sentiment, zum Zählen der positiven, negativen und neutralen Kommentare

# In[28]:


summary= df0.groupby(['team_by_entity','week']).agg(
                                   outcome=('win_for_entity', 'first'),
                                   avg_score=('score', 'mean'),
                                   count_neg=('sentiment', lambda x: count_sentiment(x, 'negative')),
                                   count_pos    =('sentiment',  lambda x: count_sentiment(x, 'positive')),
                                   count_neutral=('sentiment', lambda x: count_sentiment(x, 'neutral')))


# In[29]:


summary = summary.reset_index()


# Abschließen wird die Spielwoche in einen numerischen Wert umgewandelt. 

# In[30]:


summary['week'] = summary['week'].apply(lambda x: int(x.split()[1]))


# In[31]:


summary = summary.sort_values('week')


# In[32]:


summary


# Das Ergebniss wird in einer CSV-Datei gespeichert und im anschließenden Notebook zur Datenanalyse genutzt. 

# In[33]:


summary.to_csv("summary_2021.csv")

