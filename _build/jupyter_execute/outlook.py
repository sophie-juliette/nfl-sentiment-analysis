#!/usr/bin/env python
# coding: utf-8

# # Ausblick und Fazit

# In den vorhergenden Notebooks haben wir gezeigt, dass durch Webscrapping und Sentimentanalyse der Zusammenhang zwischen Stimmung und Leistung untersucht werden kann. Bei der Bearbeitung sind wir an verschiedene Grenzen der technischen Umsetzung gestoßen, welche wie folgt aufgelöst werden können. Ebenfalls stellen wir dar, wie der Use-Case weiterentwickelt werden kann. 

# ## Technischer Umsetzung 

# Die im Abschnitt [zukünftige Daten](gc_future) beschriebene Logik konzentrierte sich stark an dem PoC. Hier könnten Schnittstellenoptimierungen im Code erfolgen für mehr Effizenz. 
# 

# Die wesentlichste Limitierung im Projekt war das geringe Budget in Google Cloud. Dies hatte sowohl Auswirkungen auf die Youtube-API, wie auch auf die Sentiment-Analyse mit Google NLP.  
# Über einen längeren Zeitraum könnten zum Beispiel mehr Videos innerhalb der Youtube-API-Limits abgerufen werden, wenn der jeweilige PageToken wie ein Cookie in einer Textdatei gespeichert wird. Beim nächsten Durchlauf kann dieser als Startpunkt verwendet werden. Um weniger Traffic über Google NLP zu generieren, könnten beispielweise zuerst die Kommentare mit Mannschaftsnamen aus dem Synonym-Wörtbuch bestimmt werden, bevor diese mit NLP analysiert werden. 

# Zur graphischen Auswertung der Sentimentanlyse könenn die Grafiken aus dem Notebook "Datenanalyse" in ein Dashboard überführt werden. Ein Lösung in der Google Cloud, Looker, würde sich dafür anbieten. 

# ## Weiterentwicklung des Use-Case

# Das Scrapping in der Cloud ist bereits so gestaltet, dass durch einen fortlaufenden Betrieb (z.B. einmal die Woche nach Abschluss des Spieltags) die Aktualität des Dashboards gewährleistet wird. 

# Zusätzlich kann das Dashboard mit vielen weiteren Social-Media-Daten ergänzt werden. Dafür müssen Kanäle wie Instagram oder Facebook analysiert und eingebunden werden.  
# Durch „Lags“ (Zeitreihenverschiebung) kann ein Bezug zwischen Stimmung und einem vorhergenden Spiel ermittelt werden. Wie beispielsweise eine sehr positive Stimmung im Vorfeld zum eingangs vorgestellten Spiel in München 2022. {cite:p}`dw_nfl`  
# Abschließend kann auch ein Vergleich der Mannschaften untereinander im Dashboard, zu weiteren Erkenntnissen führen. 
