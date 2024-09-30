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

#  Websocket Backend Server IP
IP = "192.168.178.24"

# Debug flag to enable or disable debug output
DEBUG = False

# Initial speed of the robot
speed = 0

# Initial heading of the robot: 0 degrees is forward, 90 degrees is to the right, 180 degrees is back, and 270 is to the left
heading = 0

# Flag to indicate the direction of movement (0 for forward, 1 for reverse)
flags = 0

# Initial accelerometer data
accelerometer = {"Accelerometer": {'is_valid': True, 'X': 0, 'Y': 0, 'Z': 0}, 'IMU': {'is_valid': True, 'Pitch': 0, 'Roll': 0, 'Yaw': 0}}

# Initial velocity data
velocity = {'Velocity': {'is_valid': True, 'X': 0, 'Y': 0}}

# Initial motor stall flag status
stall_flag = {'motorIndex': 0, 'isTriggered': False}

# Get the current asyncio event loop
loop = asyncio.get_event_loop()

# Initialize the Sphero RVR with the SerialAsyncDal
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

async def motor_stall_handler(response):
    """
    Handles the motor stall response by setting the global stall_flag.

    Args:
        response: The response indicating the motor stall status.
    """
    global stall_flag
    stall_flag = response
    #print('Motor stall response:', response)

async def accelerometer_handler(accelerometer_data):
    """
    Handles incoming accelerometer data by updating the global accelerometer variable.

    Args:
        accelerometer_data (Any): The data received from the accelerometer.
    """
    global accelerometer
    accelerometer = accelerometer_data    

async def imu_handler(imu_data):
    """
    Handles incoming IMU (Inertial Measurement Unit) data.

    This function is an asynchronous handler that processes IMU data and updates
    the global `imu` variable with the provided data.

    Args:
        imu_data: The data from the IMU to be processed and stored.
    """
    global imu
    imu = imu_data
    
async def velocity_handler(velocity_data):
    """
    Handles the incoming velocity data and updates the global velocity variable.

    Args:
        velocity_data: The data representing the velocity to be handled.
    """
    global velocity
    velocity = velocity_data

async def send_camera_data():
    """
    Continuously captures video frames from the default camera, encodes them as JPEG, 
    and sends them to a WebSocket server.
    The function attempts to connect to a WebSocket server at the specified URI and 
    sends the captured frames in base64-encoded JPEG format. If the connection is 
    closed or an unexpected error occurs, it will attempt to reconnect after a short delay.
    Exceptions:
        websockets.ConnectionClosedError: If the WebSocket connection is closed unexpectedly.
        Exception: For any other unexpected errors.
    Notes:
        - The function runs indefinitely until an unexpected error occurs.
        - The function uses OpenCV for video capture and frame encoding.
        - The function uses the `websockets` library for WebSocket communication.
        - The function assumes that the `IP` variable is defined elsewhere in the code.
    """
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
    """
    Connects to a WebSocket server and listens for movement data.

    This function establishes a WebSocket connection to a server specified by the IP and port.
    It continuously listens for incoming messages containing movement data in JSON format.
    Based on the received data, it updates the `movementlist` to reflect the current state of
    key presses and releases.

    The expected JSON format for movement data is:
    {
        "type": "keydown" or "keyup",
        "key": "ArrowUp" or "ArrowDown" or "ArrowLeft" or "ArrowRight" or "Shift"
    }

    The `movementlist` is updated as follows:
    - Index 0: ArrowUp (1 for keydown, 0 for keyup)
    - Index 1: ArrowDown (1 for keydown, 0 for keyup)
    - Index 2: ArrowLeft (1 for keydown, 0 for keyup)
    - Index 3: ArrowRight (1 for keydown, 0 for keyup)
    - Index 4: Shift (1 for keydown, 0 for keyup)

    If the WebSocket connection is closed or a JSON decoding error occurs, appropriate error
    messages are printed.

    Raises:
        Exception: If the WebSocket connection cannot be established.
    """
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
    """
    Controls the movement of a robot based on the global `movementlist`.
    This function continuously checks the `movementlist` to determine the robot's
    movement direction, speed, and heading. It adjusts the speed and heading
    accordingly and sends the driving command to the robot. The function also
    ensures that the speed and heading values are within their respective limits.
    Global Variables:
    - rvr: The robot instance to control.
    - speed: The current speed of the robot.
    - heading: The current heading of the robot.
    - flags: Indicates the direction of movement (0 for forward, 1 for reverse).
    - movementlist: A list indicating the movement commands.
    - DEBUG: A flag to enable or disable debug output.
    Movement Commands in `movementlist`:
    - movementlist[0]: Move forward (1 to move forward, 0 otherwise).
    - movementlist[1]: Move backward (1 to move backward, 0 otherwise).
    - movementlist[2]: Turn left (1 to turn left, 0 otherwise).
    - movementlist[3]: Turn right (1 to turn right, 0 otherwise).
    - movementlist[4]: Speed boost (1 to enable boost, 0 otherwise).
    The function runs indefinitely, issuing driving commands every 0.1 seconds.
    Raises:
    - asyncio.CancelledError: If the task running this function is cancelled.
    """
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

        if DEBUG:
            print(movementlist)
            print("Speed:" + str(speed))
            print("Heading:" + str(heading))
            print("Flag:" + str(flags))
            
        # issue the driving command
        await rvr.drive_with_heading(speed, heading, flags)

        # sleep the infinite loop for a 10th of a second to avoid flooding the serial port.
        await asyncio.sleep(0.1)

async def send_battery():
    """
    Asynchronously sends the battery percentage to a WebSocket server at regular intervals.
    This function connects to a WebSocket server specified by the IP and port (5002),
    retrieves the battery percentage from the `rvr` object, and sends it to the server
    as a JSON-encoded message every 60 seconds. If the connection is closed, it attempts
    to reconnect after a short delay. If an unexpected error occurs, the function breaks
    out of the loop.
    Exceptions:
        websockets.ConnectionClosedError: If the WebSocket connection is closed unexpectedly.
        Exception: For any other unexpected errors.
    Note:
        The function runs indefinitely until an unexpected error occurs or the program is terminated.
    """
    uri = f"ws://{IP}:5002"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                battery_percentage = await rvr.get_battery_percentage()
                
                if DEBUG:
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
    """
    Asynchronously sends driving data to a WebSocket server.
    This function continuously attempts to connect to a WebSocket server
    specified by the global `IP` variable on port 5003. Once connected,
    it sends a JSON-encoded list containing the global variables 
    `accelerometer`, `velocity`, and a dictionary with the key 
    "motor_stall" mapped to the global `stall_flag`. The data is sent 
    every 0.8 seconds.
    If the connection is closed, it will attempt to reconnect after a 
    short delay. If any other exception occurs, it will print the error 
    and break the loop.
    Globals:
        accelerometer (any): The current accelerometer data.
        stall_flag (any): The current stall flag status.
        velocity (any): The current velocity data.
        IP (str): The IP address of the WebSocket server.
        DEBUG (bool): Flag to enable or disable debug printing.
    Exceptions:
        websockets.ConnectionClosedError: If the WebSocket connection is closed.
        Exception: For any other unexpected errors.
    """
    global accelerometer
    global stall_flag
    global velocity
    
    uri = f"ws://{IP}:5003"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                data = [accelerometer, velocity, {"motor_stall": stall_flag}]
                
                if DEBUG:
                    print(data)
                
                await websocket.send(json.dumps(data))
                await asyncio.sleep(0.8)  # 500 millisekunden
        except websockets.ConnectionClosedError as e:
            print(f"Connection closed: {e}")
            print("Reconnecting...")
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break



async def main():
    """
    Main asynchronous function to initialize and control the Robo.
    This function performs the following tasks:
    1. Wakes up the Robo.
    2. Resets the yaw of the Robo.
    3. Adds sensor data handlers for velocity, accelerometer, and IMU.
    4. Enables motor stall notifications and sets a handler for motor stall events.
    5. Starts the sensor control with a specified interval.
    6. Runs multiple tasks concurrently to handle camera data, movement data, Robo movement, battery status, and driving data.
    Global Variables:
    - rvr: The Robo object to be controlled.
    Handlers:
    - velocity_handler: Handles velocity sensor data.
    - accelerometer_handler: Handles accelerometer sensor data.
    - imu_handler: Handles IMU sensor data.
    - motor_stall_handler: Handles motor stall notifications.
    Concurrent Tasks:
    - send_camera_data: Task to send camera data.
    - receive_movement_data: Task to receive movement data.
    - move_robo: Task to control Robo movement.
    - send_battery: Task to send battery status.
    - send_driving_data: Task to send driving data.
    """
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
    
    await rvr.sensor_control.start(interval=800)
    
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



