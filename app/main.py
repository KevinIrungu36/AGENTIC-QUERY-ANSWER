from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

# Import our agent - use absolute imports
try:
    from app.agent import AIQuestionAnswerAgent
    agent_instance = AIQuestionAnswerAgent()
    print("✅ Agent initialized successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    agent_instance = None
except Exception as e:
    print(f"❌ Agent initialization error: {e}")
    agent_instance = None

app = FastAPI(
    title="AI Question-Answer Helper",
    description="A simple AI agent that answers user questions with search tool integration",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    used_tool: bool
    tool_result: Optional[str] = None
    status: str

@app.get("/")
async def root():
    return {
        "message": "AI Question-Answer Helper API is running!",
        "status": "healthy" if agent_instance else "agent_not_initialized"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint that processes user messages"""
    try:
        if not agent_instance:
            raise HTTPException(
                status_code=500, 
                detail="AI agent is not initialized. Check if GROQ_API_KEY is set correctly."
            )
            
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate response using the agent
        result = agent_instance.generate_response(request.message.strip())
        
        return ChatResponse(
            response=result["response"],
            used_tool=result["used_tool"],
            tool_result=result.get("tool_result"),
            status="success"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health_check():
    agent_status = "healthy" if agent_instance else "unhealthy"
    return {
        "status": agent_status, 
        "service": "AI Question-Answer Helper",
        "agent_initialized": agent_instance is not None
    }