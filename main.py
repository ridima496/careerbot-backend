from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import replicate
import os

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your Replicate API Token here (safely in production via environment variables)
os.environ["REPLICATE_API_TOKEN"] = "r8_AQHa0wk2DFGpJ3P3JS9OxVnhpIG9wdz1a7q6C"

@app.get("/")
def read_root():
    return {"message": "CareerBot backend with Mistral is running!"}

@app.post("/get_response")
async def get_response(request: Request):
    data = await request.json()
    message = data.get("message", "")

    output = replicate.run(
        "mistralai/mistral-7b-instruct-v0.1",
        input={
            "prompt": f"[INST] {message} [/INST]",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_new_tokens": 200
        }
    )

    response_text = ''.join(output) if isinstance(output, list) else str(output)
    return {"response": response_text}