#!/usr/bin/env python
# coding: utf-8

# # Einleitung

# ## Use Case

# >"Das war eine der großartigsten Football-Erfahrungen, die ich je gemacht habe. Dafür, dass ich seit 23 Jahren in der Liga bin, sagt das eine Menge aus. Die Fans waren unglaublich." {cite:ps}`brady_cite`
# 
# Dieses Zitat stammt vom Quaterback der Tampa Bay Buccaners nach dem ersten Spiel der regulären Season der National Football League (NFL) der USA in München. Die NFL sieht Europa als einen Zukunftsmarkt für American Football und damit wächst auch die Bedeutung als Austragungsort {cite:p}`deutschlandfunk`. Die Buccs haben das "Heimspiel" in Europa mit 21:16 gegen die Seatle Seehawks gewonnen. Zum Spiel war Football-Fans aus ganz Deutschland unabhänig von ihrer Lieblingsmannschaft anwesend und die Stimmung kam einer großen Party gleich {cite:p}`sued_nfl`. Doch ist dies bei jeden NFL-Spiel so? Oder gibt es einen Zusammenhang zwischen der Leistung der Mannschaften und Stimmung? Ziel der Projektarbeit ist es diese Beziehung zu untersuchen. 

# In[4]:


from IPython.display import YouTubeVideo
YouTubeVideo('lDFXyIrCmr0',width=560, start=105)


# Youtubevideo von {cite:ts}`yt_cr`

# ## Systeminfrastruktur
# 
# Die folgende Abbildung zeigt die geplante Struktur zur Umsetzung des Use-Case-Szenarios. Die NFL-Endergebnisse sollen verwendet werden, um die Kommentare unter den Highlightvideos auf Youtube zu analysieren. Dazu wird ein Webscrapper gebaut, welcher die Datenbank mit Spieldaten befüllt. Basierend auf diesen Daten werden die Kommentare ausgelesen und mit der Google Cloud Natural Language Processing API auf Sentimentwerte nach Entitäten untersucht. Die Ergebnisse werden anschließend auf einer lokalen Jupyter-Anwendung analysiert.
# 
# ```{figure} /images/poc_overall_vertical.drawio.png
# ---
# name: poc_overall_vertical
# ---
# Eigene Darstellung der geplanten Infrastruktur
# ```
# 
