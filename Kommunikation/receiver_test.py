import websocket
import cv2
import numpy as np

# WebSocket URL
WS_URL = "ws://localhost:5000/send-camera"

def on_message(ws, message):
    np_arr = np.frombuffer(message, dtype=np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is not None:
        cv2.imshow('Kamera Stream', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            ws.close()
            cv2.destroyAllWindows()

def on_error(ws, error):
    print(f"Fehler: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### Verbindung geschlossen ###")

def on_open(ws):
    print("### Verbindung hergestellt ###")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(WS_URL,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
