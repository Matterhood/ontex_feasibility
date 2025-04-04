from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from src.packaging_evaluation.state import PackagingEvaluationState
from src.packaging_evaluation.tools import (
    image_analysis,
    concept_breaker,
    human_feedback,
    process_feedback,
    technical_feasibility,
    operations,
    reflection,
    final_score
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationRequest(BaseModel):
    packaging_concept: str
    concept_images: List[str] = []

class EvaluationResponse(BaseModel):
    state: dict
    current_node: str
    messages: List[dict]
    process_complete: bool

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_packaging(request: EvaluationRequest):
    try:
        # Initialize state
        state = PackagingEvaluationState(
            packaging_concept=request.packaging_concept,
            concept_images=request.concept_images
        )
        
        # Process nodes until completion or human feedback needed
        while not state.process_complete and not state.awaiting_human_input:
            if state.current_node == "image_analyzer":
                state = await image_analysis(state)
            elif state.current_node == "concept_breaker":
                state = await concept_breaker(state)
            elif state.current_node == "human_feedback":
                state = await human_feedback(state)
            elif state.current_node == "process_feedback":
                state = await process_feedback(state)
            elif state.current_node == "technical_feasibility":
                state = await technical_feasibility(state)
            elif state.current_node == "operations":
                state = await operations(state)
            elif state.current_node == "reflection":
                state = await reflection(state)
            elif state.current_node == "final_score":
                state = await final_score(state)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown node: {state.current_node}")
        
        return EvaluationResponse(
            state=state.dict(),
            current_node=state.current_node,
            messages=state.messages,
            process_complete=state.process_complete
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit_feedback")
async def submit_feedback(feedback: dict):
    try:
        # This endpoint would handle user feedback
        # Implementation depends on how you want to store/process feedback
        return {"status": "success", "message": "Feedback received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 