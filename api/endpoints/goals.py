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

@router.get("/history", response_model=List[schemas.HistoryResponse])
def get_history(db: Session = Depends(get_db)):
    service = GoalService(db)
    return service.get_history()
