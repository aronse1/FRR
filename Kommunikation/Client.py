import asyncio
import websockets
import cv2
import json 
from PIL import Image
from io import BytesIO
import time

from sphero_sdk import SerialAsyncDal
from sphero_sdk import SpheroRvrAsync



IP = "192.168.178.24"

speed = 0
#heading: 0 degrees is forward, 90 degrees is to the right, 180 degrees is back, and 270 is to the left
heading = 0
flags = 0
loop = asyncio.get_event_loop()
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)



async def send_camera_data():
    uri = f"ws://{IP}:5000/send-camera"
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

#forward, backwards, left, right, brake
movementlist = [0,0,0,0,0]

async def receive_movement_data():
    uri = f"ws://{IP}:5000/receive-movement-input"
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
                    if direction["key"] == " ":
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
                    if direction["key"] == " ":
                        movementlist[4] = 0
            #print(movementlist)



async def move_robo():
    global rvr
    global speed
    global heading
    global flags

    print("Waking up Robo...")
    await rvr.wake()
    print("Woke Up")
    print("Resetting Yaw")
    await rvr.reset_yaw()
    print("Resetted Yaw")
    print("Running")
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
            # reset speed and flags, but don't modify heading.
            speed = 0
            flags = 0
            
        # check the speed value, and wrap as necessary.
        if speed > 48:
            speed = 48
        elif speed < -48:
            speed = -48

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


async def main():
    
    # Run both tasks concurrently
    await asyncio.gather(
        send_camera_data(),
        receive_movement_data(),
        move_robo()
    )


# Start the asyncio event loop
loop.run_until_complete(main())




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


