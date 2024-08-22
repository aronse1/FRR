import cv2
import websockets
import asyncio
import numpy as np
from PIL import Image
from io import BytesIO
import time

async def send_camera_data():
    uri = "ws://localhost:5000/receive-camera"  
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)  
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

         
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=50) 
            compressed_img = buffer.getvalue()


            await websocket.send(compressed_img)

            await asyncio.sleep(1/60)

        cap.release()  

asyncio.get_event_loop().run_until_complete(send_camera_data())
