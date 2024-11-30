import json
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import os
import sqlite3
from typing import List

DATABASE = "database.db"

if not os.path.exists(DATABASE):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE question_answer (
            id INTEGER PRIMARY KEY,
            question TEXT,
            answer TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()
    db.close()

app = FastAPI(debug=True)

@app.get("/health_check", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

class QuestionAnswer(BaseModel):
    question: str
    answer: str

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            prompt = await websocket.receive_text()
            llm_response = await interact_with_llm(prompt)
            store_question_answer(prompt, llm_response["response"])
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

    #TODO: 開発中のモデルに変更

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

# store question and answer in database
def store_question_answer(question: str, answer: str):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO question_answer (question, answer) 
        VALUES (?, ?)
    ''', (question, answer))
    db.commit()
    db.close()


# api for getting all question and answers if needed
@app.get("/qa", response_model=List[QuestionAnswer], tags=["Question and Answer"])
def get_all_question_answers():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('''
        SELECT question, answer FROM question_answer
    ''')
    rows = cursor.fetchall()
    db.close()
    return [{"question": row[0], "answer": row[1]} for row in rows]

@app.get("/qa/{qa_id}", response_model=QuestionAnswer, tags=["Question and Answer"])
def get_question_answer_by_id(qa_id: int):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('''
        SELECT question, answer FROM question_answer WHERE id = ?
    ''', (qa_id,))
    row = cursor.fetchone()
    db.close()
    if row:
        return {"question": row[0], "answer": row[1]}
    else:
        return {"question": "Not found", "answer": "Not found"}
