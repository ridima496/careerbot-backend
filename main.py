# CareerBot Backend using Together.ai

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Together.ai API key from environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"

@app.get("/")
def root():
    return {"message": "CareerBot backend running with Together.ai."}

# Store limited chat history in memory (per session)
chat_history = []

@app.post("/get_response")
async def get_response(request: Request):
    global chat_history
    data = await request.json()
    message = data.get("message", "")

    # Add user's message to history
    chat_history.append({"role": "user", "content": message})

    # Keep only last 5 exchanges (user + bot = 10 total entries)
    chat_history = chat_history[-10:]

    # Build context from history
    prompt = ""
    for pair in chat_history:
        role = "User" if pair["role"] == "user" else "CareerBot"
        prompt += f"{role}: {pair['content']}\n"

    prompt += "CareerBot:"  # Start bot's new response

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "prompt": prompt,
        "max_tokens": 700,
        "temperature": 0.7,
        "top_p": 0.95,
        "stop": None
    }

    response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        reply = result.get("choices", [{}])[0].get("text", "I'm not sure.")
        chat_history.append({"role": "bot", "content": reply.strip()})
        return {"response": reply.strip()}
    else:
        return {"response": "Sorry, the AI couldn't generate a response."}