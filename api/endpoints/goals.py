from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api import schemas
from api.dependencies import get_db
from api.services import GoalService

router = APIRouter()

@router.post("/predict-goal", response_model=schemas.GoalPredictionResponse)
def predict_goal(request: schemas.GoalRequest, db: Session = Depends(get_db)):
    service = GoalService(db)
    return service.predict_goal(request)

@router.post("/generate-goal-plan", response_model=schemas.GoalPlanResponse)
def generate_goal_plan(request: schemas.GoalRequest, db: Session = Depends(get_db)):
    service = GoalService(db)
    return service.generate_plan(request)

@router.put("/plan/{goal_id}", response_model=schemas.GoalPlanResponse)
def update_goal_plan(goal_id: int, request: schemas.UpdatePlanRequest, db: Session = Depends(get_db)):
    service = GoalService(db)
    try:
        return service.update_plan(goal_id, request.plan_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/history", response_model=List[schemas.HistoryResponse])
def get_history(db: Session = Depends(get_db)):
    service = GoalService(db)
    return service.get_history()

@router.post("/ask-ai", response_model=schemas.AskAIResponse)
def ask_ai(request: schemas.AskAIRequest, db: Session = Depends(get_db)):
    service = GoalService(db)
    answer = service.ask_ai(request.step_title, request.step_action, request.question)
    return schemas.AskAIResponse(answer=answer)

@router.post("/plan/{goal_id}/replan", response_model=schemas.GoalPlanResponse)
def replan_goal(goal_id: int, request: schemas.ReplanRequest, db: Session = Depends(get_db)):
    """Triggers a dynamic re-plan after a user fails a step."""
    service = GoalService(db)
    try:
        return service.replan(goal_id, request.failed_step_number, request.steps)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/goal/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    """Deletes a goal and all related data (plan, prediction)."""
    service = GoalService(db)
    try:
        service.delete_goal(goal_id)
        return {"status": "deleted", "goal_id": goal_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
