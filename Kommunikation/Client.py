import asyncio
import websockets
import cv2
import json 
from PIL import Image
from io import BytesIO
import time
async def send_camera_data():
    uri = "ws://localhost:5000/send-camera"
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

            await asyncio.sleep(1 /30)

        cap.release()

#forward, backwards, left, right
movementlist = [0,0,0,0]

async def receive_movement_data():
    uri = "ws://localhost:5000/receive-movement-input"
    async with websockets.connect(uri) as websocket:
        while True:
            movement_data = await websocket.recv()
            #print(f"Received movement data: {movement_data}")
            if movement_data:
                direction = json.loads(movement_data)
                if direction["type"] == "keydown":
                    if direction["key"] == "ArrowUp":
                        movementlist[0] = 1
                    if direction["key"] == "ArrowDown":
                        movementlist[1] = 1
                    if direction["key"] == "ArrowLeft":
                        movementlist[2] = 1
                    if direction["key"] == "ArrowRight":
                        movementlist[3] = 1
                if direction["type"] == "keyup":
                    if direction["key"] == "ArrowUp":
                        movementlist[0] = 0
                    if direction["key"] == "ArrowDown":
                        movementlist[1] = 0
                    if direction["key"] == "ArrowLeft":
                        movementlist[2] = 0
                    if direction["key"] == "ArrowRight":
                        movementlist[3] = 0
            print(movementlist)
            time.sleep(0.01)
        

async def main():
    # Run both tasks concurrently
    await asyncio.gather(
        send_camera_data(),
        receive_movement_data()
    )

# Start the asyncio event loop
asyncio.get_event_loop().run_until_complete(main())
