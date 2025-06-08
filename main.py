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

@app.get("/")
async def root():
    return {"message": "CareerBot backend is live!"}

@app.post("/get_response")
async def get_response(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()

        if not user_input:
            return {"response": "Please enter a valid message."}

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"[INST] {user_input} [/INST]"

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "prompt": prompt,
            "max_tokens": 700,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post("https://api.together.xyz/v1/completions", json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        output = result.get("choices", [{}])[0].get("text", "").strip()

        return {"response": output or "No response generated."}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"response": f"⚠️ Error: {str(e)}"}
