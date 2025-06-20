from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

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

        messages = [
            {
                "role": "system", 
                "content": """You are CareerBot..."""  # Keep your existing system prompt
            }
        ]
        
        for msg in history:
            messages.append({
                "role": "user" if msg["sender"] == "You" else "assistant",
                "content": msg["text"]
            })
        
        messages.append({"role": "user", "content": user_input})

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://your-site-url.com",
            "X-Title": "CareerBot",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/llama-3-70b-instruct",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": True
        }

        # Create a generator for streaming
        def generate():
            with requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=1024):
                    yield chunk

        return Response(content=generate(), media_type="text/event-stream")

    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] {str(e)}")
        return Response(
            content="data: " + '{"response": "⚠️ Service unavailable. Please try later."}\n\n',
            media_type="text/event-stream"
        )
    
    except Exception as e:
        print(f"[SERVER ERROR] {str(e)}")
        return Response(
            content="data: " + '{"response": "⚠️ An unexpected error occurred."}\n\n',
            media_type="text/event-stream"
        )
