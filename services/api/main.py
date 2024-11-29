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
        await websocket.send_text(f"Connected: Client {client_id}")
        while True:
            prompt = await websocket.receive_text()
            llm_response = await interact_with_llm(prompt)
            await websocket.send_text(llm_response)

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")


async def interact_with_llm(prompt: str) -> str:
    await asyncio.sleep(1)
    return f"Response to '{prompt}' from LLM"

# HTML interface
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chatbot</title>
    </head>
    <body>
        <h1>Chatbot</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/1");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)
