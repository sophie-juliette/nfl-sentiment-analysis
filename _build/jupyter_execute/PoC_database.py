#!/usr/bin/env python
# coding: utf-8

# # Datenbank

# In[10]:


import json
from pymongo import MongoClient
from bson import ObjectId


# Die Spieldaten aus dem Webscrapping und Youtube-Kommentare werden in einer mongodb-Datenbank gespeichert. Diese dient als zentrale Ablage für Daten aus Teilschritten und Endergebnis. In diesem Notebook wird das Konzept dazu erläutert. 
# 

# ## Entscheidung für NoSQL
# 
# Nachfolgend werden zwei mögliche Ideen zum Vorhalten der Daten in der mongodb-Datenbank gezeigt.
# 
# **Entwurf 1**
# 
# Die Feldnamen team1, team2, score1, score2 und week sind Ergebnisse des Webscrappings. Im ersten Entwurf sollten die Kommentare und Sentiment-Felder (hier beispielhaft mit Score und Salience) als Liste je Spiel-Dokument hinzugefügt werden.
# 
# ```
# {
#     'team1':Name1,
#     'team2':Name2,
#     'score1':16,
#     'score2':28,
#     'week':'Week 4'
#     'Kommentare Text': Liste mit Kommentaren [
#                                         'string 1', string2,...
#                                         ]
#     'Kommentare Nr Scores': Liste mit Dicts zu Entitäten [{
#                                                              'Dellas':0.4,
#                                                              'Packers':0.6,   
#                                                             }]
#     'Kommentare Nr Salience': Liste mit Dicts zu Entitäten [{
#                                                              'Dellas':0.4,
#                                                              'Packers':0.6,   
#                                                             }]
# }
# ```
# 
# **Entwurf 2**
# 
# Im zweiten Entwurf wird je Entität ein eigenes Dokument erstellt. Die Entität ist dabei das Resultat aus der später erläuterten Sentimentanalyse. Dadurch entfällt die komplexe Listenlogik und der Zugriff auf die Elemente wird erleichtert. Da alle Feldnamen bekannt sind wäre eine SQL-Datenbank aus dem Google Cloud Angebot ebenso möglich.
# 
# Die Entscheidung fällt auf Entwurf 2 mit mongoDB als NoSQL-Lösung, um die Flexibilität bei der Weiterentwicklung des Projekts zu erhalten.
# 
# ```
# {
#     'team1':Name1,
#     'team2':Name2,
#     'score1':16,
#     'score2':28,
#     'week':'Week 4'
#     
#     'videoID': String
#     
#     'Kommentar': String
#     'Entität': String
#     'Score': value
#     'Salience': value
# }
# ```

# ## Einrichtung mongodb
# 
# Als Teil der Cloud-Infrastruktur wird MongoDB als Datenbank verwendet. Diese kann über den Google Cloud Account erstellt werden und wird nach Nutzung abgerechnet.  
# Auf mongodb.com wird eine kostenloses Cluster mit 512 MB angeboten, welche nach Auswahl auf aws, Google Cloud oder Azure Cloud gehostet wird. Daher erfolgt die Registrierung auf mongodb.com und die Datenbank wird als einzige Komponente außerhalb des Google Cloud Accounts verwaltet. Die nachfolgenden Abbildungen zeigen einen Teil des Erstellprozesses.
# 
# ```{figure} /images/mongoDB_clouds.png
# ---
# name: mongoDB_clouds
# ---
# Screenshot Clouds für mongoDB {cite:p}`mongodb_info`
# ```
# 
# ```{figure} /images/mongoDB_price.png
# ---
# name: mongoDB_price
# ---
# Screenshot Preise für mongoDB {cite:p}`mongodb_info`
# ```
# 
# Die Datei API_Data.json enthält unter anderem die Zugangsdaten zur Datenbank. Nachfolgend wird eine Verbindung zu mongodb aufgebaut. Für den Proof of Concept wird eine zweiten Datenbank als in der späteren Cloud-Lösung verwendet.

# In[7]:


mongodb_pass = json.load(open('API_Data.json'))['mongoDB_pass'] # password mongodb user
client = MongoClient(mongodb_pass)

# Proof of Concept
db = client.nfl_data
mycoll = db.games

# Cloud Umgebung
db_cloud = client.gc_nfl
mycoll_cloud = db_cloud.gc_games


# ## Beispielcode
# 
# Mit folgenden Code-Snippets wird regelmäßig gearbeitet.

# In[ ]:


'''
Hinzufügen eines Dictionaries
'''
mycoll.insert_one()


# In[ ]:


'''
Hinzufügen von Testdaten
'''
test = [{'team1': 'Giants', 'week': 'Week 5', 'team2': 'Cowboys', 'year': '2021'},
{'team1': 'Rams', 'week': 'Week 5', 'team2': 'Seahawks', 'year': '2021'},
{'team1': 'Cowboys', 'score1': '16', 'team2': 'Broncos', 'score2': '30', 'year': '2021', 'week': 'Week 9'}]
mycoll.insert_many(test)


# In[ ]:


'''
Sicherung des erfolgreichen Webscrapping Durchlaufs in einer json-Datei.
'''
data = list(mycoll_cloud.find({'videoID':{'$exists':False}},{'_id':0}))
with open('backup_data.json','w') as f:
    json.dump(data,f)


# In[ ]:


'''
Löschen von Daten die im Rahmen des Testens erzeugt wurden.
Delete_many zur Sicherheit mit Trigger und Auskommentierung.
'''
trigger = False
if trigger == True:
    # mycoll.delete_many({})
    # mycoll_cloud.delete_many({'videoID':{'$exists':True}})

# id = '638b477dfa6daae7e37061d9'
# mycoll.delete_one({'_id':ObjectId(id)})

