from fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import re
import requests
import os
import json
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
        history = data.get("history", [])[-5:]

        if not user_input:
            return {"response": "Please enter a valid message."}

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        formatted_history = ""
        for msg in history:
            role = "user" if msg["sender"] == "You" else "assistant"
            formatted_history += f"{role}: {msg['text']}\n"

        prompt = f"[INST] You are CareerBot, an AI assistant that helps with career guidance. Only answer to career-related questions.\n{formatted_history}user: {user_input} [/INST]"

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
        output = output.replace('\n', '<br>')

        return {"response": output or "No response generated."}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"response": f"⚠️ Error: {str(e)}"}
