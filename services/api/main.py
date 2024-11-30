import json
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI(debug=True)

@app.get("/health_check", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            prompt = await websocket.receive_text()
            llm_response = await interact_with_llm(prompt)

            llm_response["client_id"] = client_id
            await websocket.send_text(json.dumps(llm_response))
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")

async def interact_with_llm(prompt: str) -> dict:
    urls = ["http://localhost:11434/api/generate"]
    headers = {
        "Content-Type": "application/json"
    }

    url = urls[0]
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        data = response.json()
        return {
            "response": data.get("response", "No response"),
            "created_at": data.get("created_at", "No timestamp")
        }
    else:
        return {
            "response": "Error",
            "created_at": "N/A"
        }
