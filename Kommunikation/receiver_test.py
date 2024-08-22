import websocket
import cv2
import numpy as np
import socket
import sys
# WebSocket URL
WS_URL = "ws://{ip}:5000/receive-camera"

def check_ip(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

def find_first_ip_in_network(port):
    local_ip = socket.gethostbyname(socket.gethostname())
    subnet = '.'.join(local_ip.split('.')[:-1]) + '.'

    for i in range(1, 255):
        ip = subnet + str(i)
        if check_ip(ip, port):
            return ip

    return None


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
    ip_adress = None
    if len(sys.argv) >1:
        if sys.argv[1] == "localhost":
            ip_adress = "127.0.0.1"
    else:
        ip_adress = find_first_ip_in_network(5000)

    if ip_adress:
        print(f"Verbindung zu {ip_adress}")

    websocket.enableTrace(True)
    ws_url = WS_URL.format(ip=ip_adress)
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
