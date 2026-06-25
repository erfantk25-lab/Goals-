from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class GoalRequest(BaseModel):
    title: str = Field(..., min_length=3, description="The title of the goal")
    description: str = Field(..., min_length=10, description="Detailed description of the goal")
    category: str = Field(..., description="Category of the goal e.g., Career, Health")

class GoalPredictionResponse(BaseModel):
    difficulty: str
    estimated_success_probability: float
    estimated_completion_time_days: int

class GoalPlanResponse(BaseModel):
    goal_id: Optional[int] = None
    plan_data: Dict[str, Any]
    metadata: Dict[str, Any]

class HistoryResponse(BaseModel):
    id: int
    title: str
    category: str
    created_at: datetime
    
    class Config:
        from_attributes = True
