from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(msg: Message):
    # Placeholder response
    return {"response": f"You said: {msg.message}"}