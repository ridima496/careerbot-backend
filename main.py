from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_response")
async def get_response(request: Request):
    data = await request.json()
    user_input = data.get("message", "").strip()

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "prompt": user_input,
        "max_tokens": 300,
        "temperature": 0.7,
        "top_p": 0.8,
        "stop": ["</s>", "\n"]
    }

    response = requests.post("https://api.together.xyz/v1/completions", json=payload, headers=headers)
    result = response.json()
    output = result.get("choices", [{}])[0].get("text", "").strip()

    return {"response": output}
