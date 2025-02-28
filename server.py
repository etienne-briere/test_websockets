import asyncio
import websockets # Module permettant de créer un serveur WebSocket pour envoyer les données à Unity
from bleak import BleakClient, BleakScanner
from functools import partial
import os

PORT = int(os.environ.get("PORT", 8765))  # Port défini par Render

# Adresse MAC/Bluetooth du Polar H10 (à remplacer par la tienne)
HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # UUID standard du capteur cardiaque

# Liste des clients WebSocket connectés
clients = set() # Liste des clients WebSocket connectés (Unity va s’y connecter)

async def connect_polar_h10():
    # Scan des appareils ble disponibles
    print("🔍 Scan des périphériques BLE...")
    devices = await BleakScanner.discover()

    polar_device_found = False

    for device in devices:
        if not polar_device_found:
            print(f"Nom: {device.name}, Adresse: {device.address}")  # address = UUID de l'appareil ble

        # Chercher appareil Polar parmi ceux disponibles
        if device.name is not None and "Polar" in device.name:
            polar_device_found = True

            async with BleakClient(device) as client:
                print(f"✅ Connected to {device.name}, {device.address}")

                def callback(sender, data):
                    heart_rate = data[1]
                    print(f"💓HR: {heart_rate} BPM")

                    asyncio.create_task(send_data_to_clients(heart_rate)) # envoie la valeur du rythme cardiaque aux clients WebSocket (Unity)

                await client.start_notify(HEART_RATE_UUID, callback) # Demande à recevoir les notifs du Polar H10 et d’exécuter callback() à chaque nouvelle donnée
                # Boucle infini
                while True:
                    await asyncio.sleep(1) # attendre 1sec entre chaque boucle

    if not polar_device_found:
        print("❌ No Polar device found")


async def send_data_to_clients(heart_rate):
    """Fonction asynchrone qui envoie la FC aux clients connectés"""
    if not clients:  # Vérifie si au moins un client est connecté
        print("❌ Aucun client WebSocket connecté !")
        return  # Ne fait rien si aucun client n'est connecté

    print("✅ Client WebSocket détecté, envoi des données...")
    message = str(heart_rate)
    #message = str(heart_rate).encode('utf-8')  # encode le message en bytes
    print(f"📤 Envoi de la FC : {message}")  # Vérifie que Python envoie bien la FC
    await asyncio.gather(*[client.send(message) for client in clients])  # Envoie la FC à tous les clients connectés


async def websocket_handler(websocket, path):
    """Gère la connexion avec Unity"""
    clients.add(websocket)
    #print("🔗 Unity connecté au WebSocket")
    print(f"🔗 Unity connecté (nombre total de clients : {len(clients)})")
    try:
        async for message in websocket:
            print(f"📩 Message reçu depuis Unity : {message}")
    except websockets.ConnectionClosed as e:
        print(f"⚠️ Unity s'est déconnecté : {e}") # ne marche pas
    finally:
        clients.remove(websocket)
        print("🔴 WebSocket déconnecté")


async def main(): # Fonction principale qui démarre tout le système
    # Démarre un serveur WebSocket sur localhost:8765
    #websocket_server = await websockets.serve(websocket_handler, "localhost", 8765)
    websocket_server = await websockets.serve(partial(websocket_handler, path="/"), "0.0.0.0", PORT)
    await asyncio.gather(websocket_server.wait_closed(), connect_polar_h10())


asyncio.run(main())



