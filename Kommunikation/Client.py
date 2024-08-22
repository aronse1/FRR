import cv2
import websockets
import asyncio
import numpy as np
from PIL import Image
from io import BytesIO

async def send_camera_data():
    uri = "ws://localhost:5000/receive-camera"  # Server WebSocket-URL
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)  # Webcam initialisieren (0 für Standard-Kamera)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Bild komprimieren
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=50)  # Komprimierung mit JPEG-Qualität 50%
            compressed_img = buffer.getvalue()

            # Bild über WebSocket senden
            await websocket.send(compressed_img)

            # Warte ein bisschen, um die FPS zu kontrollieren
            await asyncio.sleep(0.1)

        cap.release()  # Kamera freigeben

# Starte die asyncio Schleife
asyncio.get_event_loop().run_until_complete(send_camera_data())
