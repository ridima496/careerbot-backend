from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import replicate
import os

app = FastAPI()

# Enable frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace with your GitHub Pages domain for more security
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set token from environment variable (defined in Render dashboard)
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

# Load model + version
model = replicate.models.get("mistralai/mistral-7b-instruct-v0.1")
version = model.versions.get("ac6149c76b6caaaa8390c4050203104fc3762f545fc23c0e312795d34b2c3600")

@app.get("/")
def health_check():
    return {"message": "CareerBot backend running successfully."}

@app.post("/get_response")
async def get_response(request: Request):
    data = await request.json()
    message = data.get("message", "")

    # Use Mistral to generate response
    output = replicate.run(
        version,
        input={
            "prompt": f"[INST] {message} [/INST]",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_new_tokens": 300
        }
    )

    return {"response": "".join(output)}