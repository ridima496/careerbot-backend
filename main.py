from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, this is CareerBot backend."}

@app.post("/get_response")
async def get_response(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    # Basic response logic
    if "career" in user_message.lower():
        return {"response": "There are many career options available. Let's explore them together!"}
    elif "hello" in user_message.lower():
        return {"response": "Hello! I'm CareerBot, your personal career guide."}
    else:
        return {"response": "I'm still learning! Please try asking something related to careers or skills."}