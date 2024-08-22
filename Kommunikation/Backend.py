from flask import Flask, request, jsonify, make_response, url_for
from flask_sock import Sock
import requests
import threading
import time
app = Flask(__name__)

sock = Sock(app)
sock.init_app(app)

image_buffer = None
buffer_lock = threading.Lock()
@sock.route("/send-camera")
def sendCamera(sock):
    global image_buffer
    try:
        while True:
            with buffer_lock:
                if image_buffer:
                    sock.send(image_buffer)
            time.sleep(0.1)
    except Exception as e:
        print('Socket-Verbindung unterbrochen:', e)
        sock.close()


@sock.route("/receive-camera")
def receiveCamera(sock):
    global image_buffer
    try:
        while True:
            data = sock.receive() 
            with buffer_lock:
                image_buffer = data
    except Exception as e:
        print('Socket-Verbindung unterbrochen:', e)
        sock.close()
  
       

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
