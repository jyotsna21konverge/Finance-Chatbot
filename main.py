# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.agent import ask_agent

app = FastAPI(title="Finance Chatbot API")


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
