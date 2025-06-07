from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

# Allow CORS from frontend
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
    user_input = data.get("message", "")
    history = data.get("history", [])

    # Create prompt with last 5 user-bot pairs
    prompt = ""
    for pair in history:
        prompt += f"{pair['user']}\n{pair['bot']}\n"
    prompt += user_input

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
    output = result.get("choices", [{}])[0].get("text", "").strip()

    return {"response": output}


@app.post("/generate_title")
async def generate_title(request: Request):
    data = await request.json()
    message = data.get("message", "")

    # Ask Mistral to create a short title
    title_prompt = (
        "Generate a short, 4 to 5 word title for this conversation:\n"
        f"\"{message}\"\n\nTitle:"
    )

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "prompt": title_prompt,
        "max_tokens": 10,
        "temperature": 0.5,
        "top_p": 0.8,
        "stop": ["\n"]
    }

    response = requests.post("https://api.together.xyz/v1/completions", json=payload, headers=headers)
    result = response.json()
    output = result.get("choices", [{}])[0].get("text", "").strip()

    return {"title": output}
