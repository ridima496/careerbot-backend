from fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import re
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("OPENROUTER_API_KEY")

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
        history = data.get("history", [])[-5:]

        if not user_input:
            return {"response": "Please enter a valid message."}

        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ridima496.github.io/CareerBot/",  # ← change this to your real domain!
            "X-Title": "CareerBot"
        }

        messages = [{"role": "system", "content": "You are CareerBot, an AI assistant that helps with career guidance. Only answer career-related questions."}]
        for msg in history:
            messages.append({
                "role": "user" if msg["sender"] == "You" else "assistant",
                "content": msg["text"]
            })
        messages.append({"role": "user", "content": user_input})

        payload = {
            "model": "meta-llama/llama-3-70b-instruct:free",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        output = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        output = output.replace('\n', '<br>')

        return {"response": output or "No response generated."}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"response": f"⚠️ Error: {str(e)}"}
