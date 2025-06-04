from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import replicate
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ridima496.github.io"],  # Replace with your exact GitHub Pages URL
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Set the API token from Render's environment variable
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

@app.get("/")
def health_check():
    return {"message": "CareerBot backend running successfully."}

@app.post("/get_response")
async def get_response(request: Request):
    data = await request.json()
    message = data.get("message", "")

    # Call Replicate API to run Mistral 7B Instruct
    output = replicate.run(
        "mistralai/mistral-7b-instruct-v0.1",  # ✅ use full model name here
        input={
            "prompt": f"[INST] {message} [/INST]",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_new_tokens": 300
        }
    )

    return {"response": "".join(output)}