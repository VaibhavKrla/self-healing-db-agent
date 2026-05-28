from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import app as agent_app
from typing import Dict, Any

# Define the FastAPI application
app = FastAPI(
    title="Self-Healing SQL Agent API",
    description="Backend API for the Neuro-Symbolic SQL Generation Agent",
    version="1.0.0"
)

# Configure CORS to allow our React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with the specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    user_query: str

@app.get("/")
async def root():
    return {"message": "Self-Healing SQL Agent API is online"}

@app.post("/api/query")
async def execute_agent_query(request: QueryRequest) -> Dict[str, Any]:
    """
    Endpoint to trigger the LangGraph agent for SQL generation and execution.
    """
    try:
        # Initialize the state for the graph with all UI-required fields
        initial_state = {
            "user_query": request.user_query,
            "generated_sql": "",
            "execution_error": "",
            "retry_count": 0,
            "results": [],
            "columns": [],
            "execution_time_ms": 0.0,
            "telemetry": ["[OK] Query Received. Initializing Graph..."]
        }
        
        # Invoke the LangGraph agent
        # Note: This is a synchronous call. For high concurrency, consider wrapping in run_in_executor
        result = agent_app.invoke(initial_state)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Run the API server using uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
