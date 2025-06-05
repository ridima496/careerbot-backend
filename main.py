# CareerBot Backend using Together.ai (no memory)

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

@app.post("/get_response")
async def get_response(request: Request):
    data = await request.json()
    message = data.get("message", "")

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "prompt": f"[INST] {message} [/INST]",
        "max_tokens": 700,
        "temperature": 0.7,
        "top_p": 0.95,
        "stop": None
    }

    response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        reply = result.get("choices", [{}])[0].get("text", "Sorry, I couldn't generate a response.")
        return {"response": reply.strip()}
    else:
        return {"response": "Sorry, there was an error with the AI model."}