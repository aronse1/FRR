import asyncio
import websockets
import cv2
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

            await asyncio.sleep(1 / 60)

        cap.release()

async def receive_movement_data():
    uri = "ws://localhost:5000/receive-movement-input"
    async with websockets.connect(uri) as websocket:
        while True:
            movement_data = await websocket.recv()
            print(f"Received movement data: {movement_data}")
            time.sleep(0.01)

async def main():
    # Run both tasks concurrently
    await asyncio.gather(
        send_camera_data(),
        receive_movement_data()
    )

# Start the asyncio event loop
asyncio.get_event_loop().run_until_complete(main())
