from fastapi import FastAPI, WebSocket
import uvicorn
import os

app = FastAPI()

PORT = int(os.environ.get("PORT", 8765))  # Port défini par Render

# Liste des clients WebSocket connectés
clients = set() # Liste des clients WebSocket connectés (Unity va s’y connecter)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    print(f"🔗 Client connecté ! (Total : {len(clients)})")

    try:
        while True:
            message = await websocket.receive_text()
            print(f"📩 Message reçu : {message}")
            
            await websocket.send_text(message)  # Envoie à Unity
            print(f"Données envoyées à Unity : {message}")  # Vérifie que le serveur envoie bien la donnée
    except Exception as e:
        print(f"⚠️ Erreur WebSocket : {e}")
    finally:
        clients.remove(websocket)
        print("🔴 WebSocket déconnecté.")

@app.get("/")
def read_root():
    return {"message": "Serveur WebSocket en ligne 🚀"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port = PORT)



