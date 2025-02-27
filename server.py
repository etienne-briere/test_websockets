import asyncio
import os
import websockets
from bleak import BleakClient, BleakScanner
from functools import partial

PORT = int(os.environ.get("PORT", 8765))  # Port défini par Render

HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

clients = set()  # Stocke les clients WebSocket connectés

async def connect_polar_h10():
    """Recherche et connecte le Polar H10 en Bluetooth."""
    devices = await BleakScanner.discover()

    for device in devices:
        if device.name and "Polar" in device.name:
            async with BleakClient(device) as client:
                async def callback(sender, data):
                    heart_rate = data[1]
                    await send_data_to_clients(heart_rate)

                await client.start_notify(HEART_RATE_UUID, callback)

                while True:
                    await asyncio.sleep(1)

async def send_data_to_clients(heart_rate):
    """Envoie la fréquence cardiaque aux clients WebSocket."""
    if clients:
        message = str(heart_rate)
        await asyncio.gather(*[client.send(message) for client in clients])

async def websocket_handler(websocket, path):
    """Gère la connexion WebSocket."""
    clients.add(websocket)
    try:
        async for message in websocket:
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)

async def start_server():
    """Démarre le serveur WebSocket et la connexion BLE."""
    server = await websockets.serve(websocket_handler, "0.0.0.0", PORT)
    await asyncio.gather(server.wait_closed(), connect_polar_h10())

# Lancer le serveur au démarrage
asyncio.run(start_server())
