# Virtuelle Maschine

## Einrichtung
In den vorhergenden Kapiteln wird gezeigt, dass das Konzept aus der Einleitung mit  mongodb, Webscrapping und Sentimentanalyse umgesetzt werden kann. In diesem Notebook wird das Konzept in die Cloud übertragen. 

Die im Proof of Concept verwendete Youtube API und die Sentiment-Analyse sind Teil der Google Cloud, welche bei der Erstregistrierung ein Startguthaben anbietet. Um dieses möglichst auszunutzen, wird die weitere Scrapping-Infrastruktur ebenfalls in der Google Cloud eingerichtet.

Die "Google Virtual Machines" stellt Laufzeitumgebungen zur Verfügung, welche mit unterschiedlichen Betriebssystemen arbeiten. Für dieses Projekt wird Linux Debian verwendet. Nach Erstellen der Instanz müssen folgende Schritte durchgeführt werden. 

```
sudo apt-get install wget
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Im Anschluss muss miniconda initialisiert und die SSH Verbindung neugestartet werden. Nach erneuter Verbindung zum Terminal wird das Conda-Environment (base) im Terminal angezeigt. Jetzt können weitere Installationen durchgeführt oder Dateien hochgeladen werden. Folgende Abbildung zeigt die eingerichtete Maschine, nachdem  die benötigte Bibliotheken und Software installiert wurde.

```{figure} /images/linux_vm.png
---
name: linux_vm
---
Screenshot Virtual Machine Interface
```

Folgender Code zur Installation der Python-Bibliotheken stellt einen beispielhaften Auszug der Installation dar.

```
!conda install -y pymongo
!conda install -y beautifulsoup4
!pip install lxml
!pip install selenium
```

Zusätzliche Software,welche installiert werden muss, ist Chrome Binary und der Chromedriver.
Folgender Code wird zur Installation der aktuellsten Chrome Version verwendet. Die Installation wird angelehnt an {cite:p}`linuxchrome`.

```
sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
sudo echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
sudo apt-get -y update
sudo apt-get -y install google-chrome-stable
```

Mit ```google-chrome --version``` kann die Versionsnummer ausgegeben werden. Unsere Version startet mit 108, weshalb der kompatible chromedriver für Selenium heruntergeladen wird.

```
wget -N https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip -P
unzip ~/chromedriver_linux64.zip -d
rm ~/chromedriver_linux64.zip
```

Damit der Chromedriver vom Pythonskript gefunden werden kann, muss er in Linux und Mac Umgebungen in einen bestimmten Pfad liegen. Dadurch entfällt die Pfadangabe im Skript.

```
sudo mv -f ~/chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod 0755 /usr/local/bin/chromedriver
```

Im Anschluss an die Installation lassen sich die .py-Dateien [(siehe Kapitel Adaption)](gc_limits) auf der Umgebung ausführen.

```
python scrapping.py
```

## Terminierung

Zum terminierten Ausführen des Scrappers werden zwei Methoden verwendet.

Die Cronjobs bieten eine einfache Methode zum Starten von Skripten auf einer laufenden Instanz. Ergänzend bietet die Google Cloud einen Instanzen-Terminplan zum planen von Start- und Stoppzyklen.

Ein Cronjob verwendet die Syntax `* * * * * python script.py`, um ein Skript in jeder Minute auszuführen. Die Cronjobs können mit `crontab -e` auf der Instanz eingerichtet werden. Jedoch fehlt dem Cronjob Zugriff auf das gesamte Environment, weshalb der Selenium-Aufruf im Inneren des Skripts keinen Zugriff auf Google Chrome und den Chromedriver erhält. Dies wird durch weitere Angaben im Cronjob gelöst.

```
* * * * * export DISPLAY=:0 && export PATH=$PATH:/usr/local/bin && cd /home/markusarmbrecht/ && /home/markusarmbrecht/miniconda3/bin/python scrapping_post.py >> outputs.txt
```
Durch `export DISPLAY=:0` wird ein Arbeitsplatz aus Tastatur, Maus und Monitor angegeben {cite:p}`seleniumDisplay`.  
Mit `export PATH=$PATH:/usr/local/bin` erhält der Cronjob Zugriff auf weitere Komponenten des Environments z.B. den chromdriver. Über `cd` wird das Working Directory geöffnet und ein Verweis auf die Python-Installation ergänzt. Mit `>> output.txt` wird eine Textdatei zum Speichern des Terminaloutputs erzeugt. {cite:p}`seleniumPath`

Mit dem Instanzen-Terminplan können bestimmte Instanzen automatisch gestartet und heruntergefahren werden. Über das DropDown Menü *Häufigkeit* werden die Möglichkeiten *täglich, wöchentlich* und *monatlich* angeboten.

```{figure} /images/scheduler.png
---
name: inst_scheduler
---
Screenshot Instanzen Terminplan auf Google Cloud
```

## Sonstige Möglichkeiten

Alternativ könnte der Google Cloud Scheduler in Kombination mit Google Cloud Functions verwendet werden. Diese Lösung war nicht praktikabel, weil keine Textdatei wie die link_list.txt abgelegt werden konnte.
