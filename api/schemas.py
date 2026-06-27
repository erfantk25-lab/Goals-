from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class GoalRequest(BaseModel):
    title: str = Field(..., min_length=3, description="The title of the goal")
    description: Optional[str] = Field(default="", description="Detailed description of the goal")
    category: str = Field(..., description="Category of the goal e.g., Career, Health")
    use_rag: bool = Field(default=False, description="Enable web search for grounded plan generation")

class GoalPredictionResponse(BaseModel):
    difficulty: str
    estimated_success_probability: float
    estimated_completion_time_days: int

class GoalPlanResponse(BaseModel):
    goal_id: Optional[int] = None
    plan_data: Dict[str, Any]
    metadata: Dict[str, Any]

class UpdatePlanRequest(BaseModel):
    plan_data: Dict[str, Any]

class ReplanRequest(BaseModel):
    failed_step_number: int
    steps: List[Dict[str, Any]]

class HistoryResponse(BaseModel):
    id: int
    title: str
    category: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AskAIRequest(BaseModel):
    step_title: str
    step_action: str
    question: str

class AskAIResponse(BaseModel):
    answer: str

class DashboardMetricsResponse(BaseModel):
    total_requests: int
    error_rate: float
    total_alerts: int
    latest_drift_score: float
    avg_llm_latency_ms: float
    total_tokens_used: int
    latest_model_accuracy: float
