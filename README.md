# FRR
Fantastic RPC Robot

## Technologies

- Python
- React
- sphero SDK

## Architecture
### Verteilungsdiagram

<img src="FRR-architecture.png">

### Komponentendiagram

<img src="Komponenten.png">

## Hardware-Client

Der Sphero-Roboter wird mithilfe des Sphero SDK und Python auf einem Raspberry Pi gesteuert. Eine am Roboter befestigte Webcam überträgt einen Live-Video-Stream an das Backend. Eine 3D-gedruckte Halterung sorgt dafür, dass sowohl der Raspberry Pi als auch die Webcam stabil am Roboter montiert sind. Die Kommunikation zwischen dem Raspberry Pi und dem Roboter erfolgt über eine serielle Schnittstelle.

## Frontend

## Backend

## Challenges

### Netzwerkverbingung und Entwicklungsumgebung

Zwischen den verschiedenen Komponenten existierte keine gemeinsame Verbindung. Aus diesem Grund wurde ein WLAN-Netzwerk eingerichtet, um die Kommunikation zu ermöglichen.

### Latenz
Zu Beginn gab es eine erhebliche Verzögerung von bis zu 15 Sekunden beim Video-Stream. Die Lösung bestand darin, die Daten in Base64 umzuwandeln und auf den Einsatz eines Buffers zu verzichten, um die Übertragungsverzögerung zu minimieren.
