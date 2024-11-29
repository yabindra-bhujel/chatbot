from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio

app = FastAPI()

# Health check endpoint
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
            await websocket.send_text(llm_response)

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")


async def interact_with_llm(prompt: str) -> str:

    # どうやってLLMとやりとりするかな
    await asyncio.sleep(2)
    return f"Response to '{prompt}' from LLM"