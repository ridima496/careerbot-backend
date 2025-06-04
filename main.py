from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import replicate
import os

app = FastAPI()

# Allow GitHub Pages frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your Replicate API token here
os.environ["REPLICATE_API_TOKEN"] = "r8_8TH5JQZvT2phuHeVmfR2HLJgyQdDTuv2FPztz"

model = replicate.models.get("mistralai/mistral-7b-instruct-v0.1")
version = model.versions.get("ac6149c76b6caaaa8390c4050203104fc3762f545fc23c0e312795d34b2c3600")

@app.post("/get_response")
async def get_response(request: Request):
    data = await request.json()
    message = data.get("message", "")

    output = replicate.run(
        version,
        input={
            "prompt": f"[INST] {message} [/INST]",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_new_tokens": 200
        }
    )

    # Join output list into a single string
    return {"response": "".join(output)}