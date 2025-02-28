import asyncio
import websockets # Module permettant de créer un serveur WebSocket pour envoyer les données à Unity
import os
from functools import partial


PORT = int(os.environ.get("PORT", 8765))  # Port défini par Render

# Liste des clients WebSocket connectés
clients = set() # Liste des clients WebSocket connectés (Unity va s’y connecter)

async def websocket_handler(websocket, path):
    """Gère les connexions WebSocket"""
    clients.add(websocket)
    #print("🔗 Unity connecté au WebSocket")
    print(f"🔗 Nouveau client connecté ! (Total : {len(clients)})")
    try:
        async for message in websocket:
            print(f"📩 Message reçu depuis Unity : {message}")
    except websockets.ConnectionClosed :
        print(f"⚠️ Client déconnecté ") # ne marche pas
    finally:
        clients.remove(websocket)
        print("🔴 WebSocket déconnecté")


async def start_server(): # Fonction principale qui démarre tout le système
    # Démarre un serveur WebSocket sur localhost:8765
    #websocket_server = await websockets.serve(websocket_handler, "localhost", 8765)
    websocket_server = await websockets.serve(partial(websocket_handler, path="/"), "0.0.0.0", PORT)
    print("🚀 Serveur WebSocket en ligne sur ws://0.0.0.0:8765")
    await asyncio.Future()  # Garde le serveur actif

if __name__ == "__main__":
    asyncio.run(start_server())



