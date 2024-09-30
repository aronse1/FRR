# FRR
Fantastic RPC Robot

## Technologies

- Python
- React
- sphero SDK

## Architecture
Verteilungsdiagram
<img src="FRR-architecture.png">

Komponentendiagram
<img src="Komponenten.png">


## Hardware-Client
Using the sphero SDK and Python on a Raspberry Pi, we can control the robot.
A webcam fixed to the robot will stream a live video to the backend.
3D-printed fixture will keep the Raspberry Pi and the webcam in place.
Communication from the Raspberry Pi to the robot works with a serial interface.

## Frontend

## Backend

## Challenges

### IDE
Theres no common connection between the components.
That's why we set up a WLAN network.

### Latency
There was a huge delay (15sec) for the video.
Solution: data transformed into Base64 and stopped using a buffer.
