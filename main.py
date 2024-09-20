from autogen import AssistantAgent, UserProxyAgent
from agents import planner, assistant
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Process the chat request
        result = assistant.initiate_chat(planner, message=request.query, max_turns=2)
        return {"bot_message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=3000)
