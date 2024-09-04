


import cv2
import asyncio
import websockets
import base64
import numpy as np
WS_URL = "ws://localhost:5000"
async def receive_webcam_frames(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            
            # Base64-decodiertes Bild in ein Numpy-Array umwandeln
            jpg_original = base64.b64decode(message)
            jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
            img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)

            # Bild anzeigen
            cv2.imshow("Receiver", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

# WebSocket-Server-Adresse
asyncio.get_event_loop().run_until_complete(receive_webcam_frames(WS_URL))
