from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

@app.get("/")
def read_root():
    return {"message": "CareerBot backend running with Together.ai!"}

@app.post("/get_response")
async def get_response(request: Request):
    data = await request.json()
    prompt = data.get("message")

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "stop": ["</s>"]
    }

    response = requests.post("https://api.together.xyz/v1/completions", json=payload, headers=headers)
    result = response.json()

    output = result.get("choices", [{}])[0].get("text", "")
    return {"response": output.strip()}