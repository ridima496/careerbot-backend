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
                "content": """You are CareerBot, and you specialize in career guidance. 
                Provide help on topics like:
                - Entrance exams like JEE, NEET, CUET, etc.
                - Emerging career options
                - Career counselling for school students
                - General career advice
                - Information about a certain career
                - College search
                - Internships
                - Resume/CV writing
                - Interview preparation
                - Career path guidance
                - Skill development
                - Job search strategies
                - LinkedIn profile optimization
                
                For non-career related questions, politely decline to answer.
                If you don't know an answer to a question, tell that you're being developed, and ask the user to search on the web, politely."""
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
            "HTTP-Referer": "https://ridima496.github.io/CareerBot/",
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
                for chunk in response.iter_lines():
                    if chunk:
                        decoded_line = chunk.decode('utf-8')
                        if decoded_line.startswith('data:') and '[DONE]' not in decoded_line:
                            yield decoded_line + '\n\n'

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
