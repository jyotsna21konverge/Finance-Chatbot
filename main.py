# main.py
from typing import cast, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.agent import ask_agent

app = FastAPI(title="Finance Chatbot API")

# CORS configuration origin whitelisting for production; allowing all for development
origins = [
    "http://localhost:5173",      # Vite React
    "http://localhost:3000",      # React default
    "http://localhost:8501",      # Streamlit
    "http://localhost:8000",      # FastAPI itself
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    cast(Any, CORSMiddleware),
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],          # allows OPTIONS, POST, GET, etc
    allow_headers=["*"],          # allows all headers
)


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat_with_finance_bot(request: ChatRequest):
    try:
        answer = ask_agent(request.message)
        return {"status": "success", "response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
