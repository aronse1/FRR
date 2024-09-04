import asyncio
import websockets
import cv2
import json 
from PIL import Image
from io import BytesIO
import time
import numpy as np
import threading
from sphero_sdk import SerialAsyncDal
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import RvrStreamingServices
import base64
from sphero_sdk import BatteryVoltageStatesEnum as VoltageStates


IP = "192.168.178.24"

speed = 0
#heading: 0 degrees is forward, 90 degrees is to the right, 180 degrees is back, and 270 is to the left
heading = 0
flags = 0
accelerometer = {"Accelerometer": {'is_valid': True, 'X': 0, 'Y': 0, 'Z': 0}, 'IMU': {'is_valid': True, 'Pitch': 0, 'Roll': 0, 'Yaw': 0}}
velocity = {'Velocity': {'is_valid': True, 'X': 0, 'Y': 0}}
stall_flag = {'motorIndex': 0, 'isTriggered': False}
loop = asyncio.get_event_loop()
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

async def motor_stall_handler(response):
    global stall_flag
    stall_flag = response
    #print('Motor stall response:', response)

async def accelerometer_handler(accelerometer_data):
    global accelerometer
    accelerometer = accelerometer_data    
    #print('Accelerometer data response: ', accelerometer)

async def imu_handler(imu_data):
    global imu
    imu = imu_data
    #print('Accelerometer data response: ', imu)
    
async def velocity_handler(velocity_data):
    global velocity
    velocity = velocity_data
    print('Velocity data response:', velocity_data)

async def send_camera_data():
    uri = f"ws://{IP}:5000"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                cap = cv2.VideoCapture(0)

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    _, buffer = cv2.imencode('.jpg', frame)
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

                    await websocket.send(jpg_as_text)
                    await asyncio.sleep(0.01)  # 10ms

                cap.release()

        except websockets.ConnectionClosedError as e:
            print(f"Connection closed: {e}")
            print("Reconnecting...")
            await asyncio.sleep(2)  

        except Exception as e:
            print(f"Unexpected error: {e}")
            break


#forward, backwards, left, right, brake
movementlist = [0,0,0,0,0]

async def receive_movement_data():
    uri = f"ws://{IP}:5001"
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    movement_data = await websocket.recv()
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
                            if direction["key"] == "Shift":
                                movementlist[4] = 1
                        if direction["type"] == "keyup":
                            if direction["key"] == "ArrowUp":
                                movementlist[0] = 0
                            if direction["key"] == "ArrowDown":
                                movementlist[1] = 0
                            if direction["key"] == "ArrowLeft":
                                movementlist[2] = 0
                            if direction["key"] == "ArrowRight":
                                movementlist[3] = 0
                            if direction["key"] == "Shift":
                                movementlist[4] = 0
                except websockets.ConnectionClosed as e:
                    print(f"Connection closed: {e}")
                    break
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON: {e}")
    except Exception as e:
        print(f"Failed to connect to the WebSocket server: {e}")

async def move_robo():
    global rvr
    global speed
    global heading
    global flags
    MAX_SPEED = 155

    while True: 

        if movementlist[0] == 1 and movementlist[1] == 0:
            # if previously going reverse, reset speed back to 64
            if flags == 1:
                speed = 32
            else:
                speed +=64
            # go forward
            flags = 0
        else:
            speed = 0
        if movementlist[1] == 1 and movementlist[0] == 0:
            # if previously going forward, reset speed back to 64
            if flags == 0:
                speed = 32
            else:
                speed +=64
            # go reverse
            flags = 1
        #else:
        #    speed = 0
        if movementlist[2] == 1:
            # turning left
            heading -= 20
        if movementlist[3] == 1:
            # turning right
            heading += 20
        if movementlist[4] == 1:
            MAX_SPEED = 200
        if movementlist[4] == 0:
            MAX_SPEED = 80
            # reset speed and flags, but don't modify heading.
            
        # check the speed value, and wrap as necessary.
        if speed > MAX_SPEED:
            speed = MAX_SPEED
        elif speed < -MAX_SPEED:
            speed = -MAX_SPEED

        # check the heading value, and wrap as necessary.
        if heading > 359:
            heading = heading - 359
        elif heading < 0:
            heading = 359 + heading

        print(movementlist)
        print("Speed:" + str(speed))
        print("Heading:" + str(heading))
        print("Flag:" + str(flags))
        # issue the driving command
        await rvr.drive_with_heading(speed, heading, flags)

        # sleep the infinite loop for a 10th of a second to avoid flooding the serial port.
        await asyncio.sleep(0.1)

async def send_battery():
    uri = f"ws://{IP}:5002"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                battery_percentage = await rvr.get_battery_percentage()
                print('Battery percentage: ', battery_percentage)

                await websocket.send(json.dumps(battery_percentage))
                await asyncio.sleep(60)  # 1min
        except websockets.ConnectionClosedError as e:
            print(f"Connection closed: {e}")
            print("Reconnecting...")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
        
async def send_driving_data():
    global accelerometer
    global stall_flag
    global velocity
    
    uri = f"ws://{IP}:5003"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                data = [accelerometer, velocity, {"motor_stall": stall_flag}]
                
                print(data)
                
                await websocket.send(json.dumps(data))
                await asyncio.sleep(1)  # 250 seconds
        except websockets.ConnectionClosedError as e:
            print(f"Connection closed: {e}")
            print("Reconnecting...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break



async def main():
    global rvr
    print("Waking up Robo...")
    await rvr.wake()
    print("Woke Up")
    print("Resetting Yaw")
    await rvr.reset_yaw()
    print("Running")
    
            # Give RVR time to wake up
    await asyncio.sleep(2)
    
    await rvr.sensor_control.add_sensor_data_handler(
        service=RvrStreamingServices.velocity,
        handler=velocity_handler
    )
    
    await rvr.sensor_control.add_sensor_data_handler(
        service=RvrStreamingServices.accelerometer,
        handler=accelerometer_handler
    )
    
    await rvr.sensor_control.add_sensor_data_handler(
        service=RvrStreamingServices.imu,
        handler=imu_handler
    )
    
    
    
    await rvr.enable_motor_stall_notify(is_enabled=True)

    await rvr.on_motor_stall_notify(handler=motor_stall_handler)
    
    await rvr.sensor_control.start(interval=250)
    
    # Run both tasks concurrently
    await asyncio.gather(
        send_camera_data(),
        receive_movement_data(),
        move_robo(),
        send_battery(),
        send_driving_data(),
    )


# Start the asyncio event loop
loop.run_until_complete(main())
rvr.close()
rvr.sensor_control.clear()



# async def main():
#     global rvr

#     # Initialize the RVR before starting the main event loop
#     rvr = SpheroRvrAsync(
#         dal=SerialAsyncDal(
#             loop=asyncio.get_event_loop()
#         )
#     )
    
#     # Run both tasks concurrently
#     await asyncio.gather(
#         send_camera_data(),
#         receive_movement_data(),
#         move_robo()
#     )

# # Start the asyncio event loop
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())


