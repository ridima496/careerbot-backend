from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserQuery(BaseModel):
    question: str

@app.post("/ask")
def ask_question(query: UserQuery):
    # Placeholder response
    return {"answer": f"You asked: {query.question}"}