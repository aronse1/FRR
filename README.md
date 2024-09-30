# FRR
Fantastic RPC Robot
\n
Repo: [Github](https://github.com/aronse1/FRR)
## Technologies

- Python
- Reac
- sphero SDK

## Architecture
### Verteilungsdiagram

<img src="FRR-architecture.png">

### Komponentendiagram

<img src="Komponenten.png">

## Hardware-Client

Der Sphero-Roboter wird mithilfe des Sphero SDK und Python auf einem Raspberry Pi gesteuert. Eine am Roboter befestigte Webcam überträgt einen Live-Video-Stream an das Backend. Eine 3D-gedruckte Halterung sorgt dafür, dass sowohl der Raspberry Pi als auch die Webcam stabil am Roboter montiert sind. Die Kommunikation zwischen dem Raspberry Pi und dem Roboter erfolgt über eine serielle Schnittstelle.

Auf dem Raspberry Pi läuft die Python Anwendung, welche als Benutzerschnittstelle genutzt wird, so wird zum Start eine Verbindung auf das Netzwerk ``robowifi`` hergestellt. Beim Start der Anwendung wird nun eine Websocket Verbindung zu dem Backend herrgestellt. Dabei werden alle zwei Sekunden Sensorwerte übertragen. Die IMU ist dabei der am häufigsten abgefragte Sensor, da dieser wichtige Bewegungsdaten liefert. Werte sind dabei Himmelsrichtung, Beschleunigung und die Geschwindigkeit. 

Über das Frontend werden nun der Tastaturdruck übermittelt. Der Client wertet diesen aus und sendet Befehle an die Tank Drive Engine, welche mithilfe einer State Machine die Richtung und Geschwindigkeit des Roboters kontrolliert. Als Methode wird drive with heading verwendet, was die Richtung über den Magnetometer bestimmt ![[1]](https://github.com/sphero-inc/sphero-sdk-raspberrypi-python/blob/master/docs/SpheroRVRControlSystemManual.pdf).

### Anwendung starten
1. Eine SSH Verbindung muss zum Roboter hergestellt werden.
2. Die IP Adresse auf den der Client zugreift muss konfiguriert sein. Diese kann innerhalb der ``Client.py`` eingestellt werden.
3. Eine Virtual Enviroment muss angelegt werden. Dies kann über folgendes [Tutorial](https://docs.python.org/3/library/venv.html) durchgeführt werden.
4. Die Anwendung kann gestartet werden ``python Kommunikation/Client.py``

## Frontend

### Beschreibung der Frontend-Komponenten:
Camera.js: Diese Komponente stellt den Video-Feed des Roboters dar. Sie verbindet sich über eine WebSocket-Verbindung zum Backend, um den Live-Stream von der am Roboter befestigten Kamera zu empfangen. Die WebSocket-Verbindung wird in der startWebSocket-Funktion initialisiert, und wenn die Komponente nicht mehr benötigt wird oder geschlossen wird, wird die Verbindung mit stopWebSocket ordnungsgemäß geschlossen.

Controller.js: Diese Komponente enhält die Logik zur Steuerung des Roboters. Hier können die Tastaturbefehle erfasst und an das Backend gesendet werden, um Bewegungen oder Aktionen des Roboters auszulösen.

Header.js & Sidebar.js: Diese Komponenten sind für das Layout der Benutzeroberfläche verantwortlich, indem sie den Header und eine Sidebar des Dashboards darstellen.

Home.js: Dies ist die Hauptseite der Anwendung, die die verschiedenen Komponenten wie Camera, Controller, und Sidebar zusammenführt.

### Schritte zum Starten des Frontend-Projekts:

#### Voraussetzungen:
Node.js muss auf dem lokalen System installiert sein. npm (Node Package Manager) wird ebenfalls benötigt, was normalerweise zusammen mit Node.js installiert wird.

#### Installation und Start:
Projekt lokal klonen oder herunterladen: Stellen Sie sicher, dass die Quellcodes auf Ihrem lokalen Rechner vorliegen. Navigieren Sie dazu über das Terminal in das Projektverzeichnis.

"npm install"

Dieser Befehl installiert alle notwendigen Abhängigkeiten, die im package.json definiert sind. Sobald die Abhängigkeiten installiert sind, kann der Entwicklungsserver gestartet werden. Verwenden Sie folgenden Befehl:

"npm start"

Dies startet das Frontend im Entwicklungsmodus. Die Anwendung wird standardmäßig auf http://localhost:3000 zugänglich sein.


Hinweise:
Wenn Änderungen am Code vorgenommen werden, wird das Projekt automatisch neu kompiliert und aktualisiert.
Um die Anwendung für die Produktion bereitzustellen, können Sie den Befehl npm run build verwenden, der ein optimiertes Build-Paket erstellt.

## Backend
Das Backend befindet sich im Ordner ````/kommunikation/Backend.py```. Der Backend Server ist die Schnittstelle zwischen dem Roboter und dem Frontend. Dieser Stellt 4 Websocket Verbindungen bereit über den der Roboter und das Frontend kommuniziert.
Da der Roboter oft für das Frontend zu komplexe JSON Pakete überträgt, werden diese im Backend auch noch vereinfacht.

Das Backend kann mit 
```bash
python Backend.py 
```
gestartet werden.

## Challenges

### Netzwerkverbingung und Entwicklungsumgebung

Zwischen den verschiedenen Komponenten existierte keine gemeinsame Verbindung. Aus diesem Grund wurde ein WLAN-Netzwerk eingerichtet, um die Kommunikation zu ermöglichen.

### Latenz
Zu Beginn gab es eine erhebliche Verzögerung von bis zu 15 Sekunden beim Video-Stream. Die Lösung bestand darin, die Daten in Base64 umzuwandeln und auf den Einsatz eines Buffers zu verzichten, um die Übertragungsverzögerung zu minimieren.
