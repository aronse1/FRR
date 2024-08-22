from flask import Flask, request, jsonify, make_response, url_for
from flask_sock import Sock
import requests
import threading
import time
import asyncio

app = Flask(__name__)

sock = Sock(app)
sock.init_app(app)

frames_per_second = 60
image_buffer = "No picture"
input_buffer = "idle"
image_buffer_lock = threading.Lock()
input_buffer_lock = threading.Lock()

@sock.route("/receive-camera")
def sendCamera(sock):
    global image_buffer
    try: 
        while True:
            with image_buffer_lock:
                if image_buffer:
                    sock.send(image_buffer)
            time.sleep(1/frames_per_second)
    except Exception as e:
        sock.close()


@sock.route("/send-camera")
def receiveCamera(sock):
    global image_buffer
    try:
        while True:
            data = sock.receive() 
            with image_buffer_lock:
                image_buffer = data
    except Exception as e:
        image_buffer = "No picture"
        print('Socket-Verbindung unterbrochen:', e)
        sock.close()
  
@sock.route("/receive-movement-input")
def receiveMovement(sock):
    global input_buffer
    try: 
        while True:
            with input_buffer_lock:
                if not input_buffer == "idle":
                    sock.send(input_buffer)
            time.sleep(0.1)
    except Exception as e:
        input_buffer = "idle"
        print('Socket-Verbindung unterbrochen:', e)
        sock.close()

@sock.route("/send-movement-input")
def sendMovement(sock):
    global input_buffer
    try:
        while True:
            data = sock.receive()
            with input_buffer_lock:
                input_buffer = data
    except Exception as e:
        input_buffer = "idle"
        print('Socket-Verbindung unterbrochen:', e)
        sock.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
