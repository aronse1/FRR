
import asyncio
import websockets


connected_image_clients = set()
connected_movement_clients = set()

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
    except websockets.ConnectionClosed:
        print(f"Client {websocket} disconnected")
    finally:
        connected_movement_clients.remove(websocket)

async def main():
    image_server = await websockets.serve(image_handler, "0.0.0.0", 5000)
    movement_server = await websockets.serve(movement_handler, "0.0.0.0", 5001)

    await asyncio.gather(image_server.wait_closed(), movement_server.wait_closed())


asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()

