from fastapi import FastAPI, WebSocket
from typing import List 
import uvicorn
import os

app = FastAPI()

PORT = int(os.environ.get("PORT", 8765))  # Port défini par Render

# Stocke les connexions WebSocket ouvertes
clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    #clients.add(websocket)
    #print(f"🔗 Client connecté ! (Total : {len(clients)})")
    clients.append(websocket)  # Ajoute le client à la liste
    print(f"✅ Client connecté. Nombre total : {len(clients)}")
    
    try:
        while True:
            message = await websocket.receive_text() # reçoit du client Python
            print(f"📩 Message reçu : {message}")
            
            # Envoie à tous les clients connectés (y compris Unity)
            for client in clients:
                if client != websocket:  # Évite de renvoyer à l'expéditeur
                    await client.send_text(message)
                    print(f"📤 Données envoyées à Unity : {message}")
    
    except Exception as e:
        print(f"⚠️ Erreur WebSocket : {e}")
    finally:
        clients.remove(websocket) # Retire le client s'il se déconnecte
        print("🔴 Client déconnecté. Nombre restant : {len(clients)}")

@app.get("/")
def read_root():
    return {"message": "Serveur WebSocket en ligne 🚀"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port = PORT)



