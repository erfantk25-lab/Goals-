from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from api.dependencies import get_db
from db.models import Feedback, GoalPlan
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class FeedbackRequest(BaseModel):
    goal_plan_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comments: str | None = None

class FeedbackResponse(BaseModel):
    id: int
    message: str

@router.post("/", response_model=FeedbackResponse)
def submit_feedback(feedback_in: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit user feedback on a generated goal plan for continuous improvement."""
    
    plan = db.query(GoalPlan).filter(GoalPlan.id == feedback_in.goal_plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="GoalPlan not found")
        
    feedback = Feedback(
        goal_plan_id=feedback_in.goal_plan_id,
        rating=feedback_in.rating,
        comments=feedback_in.comments
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    logger.info(f"Received feedback (Rating: {feedback.rating}) for GoalPlan ID {feedback.goal_plan_id}")
    
    return FeedbackResponse(id=feedback.id, message="Feedback submitted successfully. Thank you!")
