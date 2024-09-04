
import asyncio
import websockets
import json
import math

connected_image_clients = set()
connected_movement_clients = set()
conected_battery_clients = set()
connected_information_clients = set()

last_movement_message = "idle"

async def image_handler(websocket, path):
    connected_image_clients.add(websocket)
    try:
        async for message in websocket:
            tasks = []
            for client in connected_image_clients:
                if client != websocket:
                    try:
                        tasks.append(asyncio.create_task(client.send(message)))
                    except websockets.ConnectionClosed:
                        connected_image_clients.remove(client)
            if tasks:
                await asyncio.wait(tasks)
    except websockets.ConnectionClosedError:
        print(f"Client {websocket} disconnected had an error")
    except websockets.ConnectionClosed:
        print(f"Client {websocket} disconnected")
    finally:
        connected_image_clients.remove(websocket)




async def movement_handler(websocket, path):
    global last_movement_message
    connected_movement_clients.add(websocket)
    try:
        async for message in websocket:
            # Nachricht nur senden, wenn sie sich von der letzten unterscheidet
            if message != last_movement_message:
                tasks = []
                for client in connected_movement_clients:
                    if client != websocket:
                        try:
                            tasks.append(asyncio.create_task(client.send(message)))
                        except websockets.ConnectionClosed:
                            connected_movement_clients.remove(client)
                if tasks:
                    await asyncio.wait(tasks)

                # Aktualisiere die letzte Nachricht
                last_movement_message = message
    except websockets.ConnectionClosedError:
        print(f"Client {websocket} disconnected had an error")
    except websockets.ConnectionClosed:
        print(f"Client {websocket} disconnected")
    finally:
        connected_movement_clients.remove(websocket)


async def battery_handler(websocket, path):
    conected_battery_clients.add(websocket)
    try:
        async for message in websocket:
            tasks = []
            for client in conected_battery_clients:
                if client != websocket:
                    try:
                        tasks.append(asyncio.create_task(client.send(message)))
                    except websockets.ConnectionClosed:
                        connected_image_clients.remove(client)
            if tasks:
                await asyncio.wait(tasks)
    except websockets.ConnectionClosedError:
        print(f"Client {websocket} disconnected had an error")
    except websockets.ConnectionClosed:
        print(f"Client {websocket} disconnected")
    finally:
        conected_battery_clients.remove(websocket)


async def information_handler(websocket, path):
    connected_information_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                #print(data)
                formatted_message = await process_message(data)
                tasks = []
                for client in connected_information_clients:
                    if client != websocket:
                        tasks.append(asyncio.create_task(client.send(formatted_message)))
                if tasks:
                    await asyncio.wait(tasks)
            except (json.JSONDecodeError, KeyError):
                print("Error parsing or processing message")
    except websockets.ConnectionClosedError:
        print(f"Client {websocket} disconnected had an error")
    except websockets.ConnectionClosed:
        print(f"Client {websocket} disconnected")
    finally:
        connected_information_clients.remove(websocket)

async def process_message(data):
    accelerometer_data = data[0]["Accelerometer"]
    imu_data = data[0]["IMU"]
    velocity_data = data[1]["Velocity"]
    motor_stall_data = data[2]["motor_stall"]
    
    if accelerometer_data["is_valid"]:
        x = accelerometer_data["X"]
        y = accelerometer_data["Y"]
        z = accelerometer_data["Z"]
        accelerometer_avg = math.sqrt(x**2 + y**2 + z**2)
    else:
        accelerometer_avg = 0
    if velocity_data["is_valid"]:
        geschwindigkeit = math.sqrt(velocity_data['X']**2 + velocity_data['Y']**2) /100000000
    else:
        geschwindigkeit = 0
    imu_yaw = imu_data["Yaw"] if imu_data["is_valid"] else 0
    if motor_stall_data != 0:
       motor_stall= motor_stall_data['isTriggered']
    else:
        motor_stall = False
    formatted_data = {
        "imu_string": winkel_zu_kompass(round(imu_yaw, 2)),
        "accelerometer": round(accelerometer_avg,2),
        "velocity": round(geschwindigkeit, 2),
        "motor_stall": motor_stall
    }
    print(formatted_data)
    return json.dumps(formatted_data)


def winkel_zu_kompass(winkel):
    if -22.5 <= winkel < 22.5:
        return "N"
    elif 22.5 <= winkel < 67.5:
        return "NE"
    elif 67.5 <= winkel < 112.5:
        return "E"
    elif 112.5 <= winkel < 157.5:
        return "SE"
    elif (157.5 <= winkel <= 180) or (-180 <= winkel < -157.5):
        return "S"
    elif -157.5 <= winkel < -112.5:
        return "SW"
    elif -112.5 <= winkel < -67.5:
        return "W"
    elif -67.5 <= winkel < -22.5:
        return "NW"
    else:
        return "N"

async def main():
    image_server = await websockets.serve(image_handler, "0.0.0.0", 5000)
    movement_server = await websockets.serve(movement_handler, "0.0.0.0", 5001)
    battery_server = await websockets.serve(battery_handler, "0.0.0.0", 5002)
    information_server = await websockets.serve(information_handler, "0.0.0.0", 5003)
    await asyncio.gather(image_server.wait_closed(), movement_server.wait_closed(), battery_server.wait_closed(), information_server.wait_closed())


asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()

