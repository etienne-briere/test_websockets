import asyncio
import websockets

async def server(websocket, path):
    print("Client connecté")
    async for message in websocket:
        print(f"Message reçu : {message}")
        await websocket.send(f"Reçu : {message}")

start_server = websockets.serve(server, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
