from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agents.orchestrator import Orchestrator
from langchain.llms import OpenAI
from services.storage import get_state, save_state
from services.monitoring import get_activities
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = OpenAI(temperature=0.3, model_name="gpt-3.5-turbo")

class ResearchRequest(BaseModel):
    topic: str
    depth: str = "balanced"

class ResearchTask(BaseModel):
    id: str
    topic: str
    status: str
    progress: float

@app.post("/research", response_model=ResearchTask)
async def create_research_task(request: ResearchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # Save initial state
    save_state(task_id, "status", {
        "topic": request.topic,
        "status": "pending",
        "progress": 0
    })
    
    # Start background task
    background_tasks.add_task(execute_research, task_id, request.topic)
    
    return {
        "id": task_id,
        "topic": request.topic,
        "status": "pending",
        "progress": 0
    }

@app.get("/research/{task_id}/status", response_model=ResearchTask)
async def get_task_status(task_id: str):
    state = get_state(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task_id,
        "topic": state.get("topic"),
        "status": state.get("status", "unknown"),
        "progress": state.get("progress", 0)
    }

@app.get("/research/{task_id}/report")
async def get_research_report(task_id: str):
    report = get_state(task_id, "report")
    if not report:
        raise HTTPException(status_code=404, detail="Report not ready or not found")
    
    return report

@app.get("/research/{task_id}/activity")
async def get_task_activity(task_id: str):
    activities = get_activities(task_id)
    return {"activities": activities}

async def execute_research(task_id: str, topic: str):
    try:
        save_state(task_id, "status", {
            "status": "in_progress",
            "progress": 0.2
        })
        
        orchestrator = Orchestrator(llm)
        
        save_state(task_id, "status", {
            "status": "researching",
            "progress": 0.4
        })
        
        result = await orchestrator.execute_research(topic)
        
        save_state(task_id, "report", result)
        save_state(task_id, "status", {
            "status": "completed",
            "progress": 1.0
        })
        
    except Exception as e:
        save_state(task_id, "status", {
            "status": "failed",
            "error": str(e),
            "progress": 0.0
        })