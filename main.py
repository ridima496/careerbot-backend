from fastapi import FastAPI, Request 
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

        # Prepare the messages for the API
        messages = [
            {
                "role": "system", 
                "content": """You are CareerBot, an AI assistant specializing in career guidance. 
                Provide helpful, professional advice on topics like:
                - Resume/CV writing
                - Interview preparation
                - Career path guidance
                - Skill development
                - Job search strategies
                - LinkedIn profile optimization
                - Salary negotiation
                - Career changes
                
                For non-career related questions, politely decline to answer."""
            }
        ]
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": "user" if msg["sender"] == "You" else "assistant",
                "content": msg["text"]
            })
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://your-site-url.com",  # Required by OpenRouter
            "X-Title": "CareerBot",                       # Required by OpenRouter
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/llama-3-70b-instruct:nitro",  # Updated model name
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # Add timeout
        )
        
        response.raise_for_status()  # Will raise HTTPError for 4XX/5XX responses
        result = response.json()
        
        output = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        # Format the output for HTML display
        formatted_output = output.replace('\n', '<br>')
        
        return {"response": formatted_output or "No response generated."}

    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] {str(e)}")
        return {"response": "⚠️ Sorry, I'm having trouble connecting to the career guidance service. Please try again later."}
    
    except Exception as e:
        print(f"[SERVER ERROR] {str(e)}")
        return {"response": "⚠️ An unexpected error occurred. Please try again."}
