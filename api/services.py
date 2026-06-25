import logging
from sqlalchemy.orm import Session
from api.schemas import GoalRequest, GoalPredictionResponse, GoalPlanResponse
from ml.model import GoalDifficultyPredictor
from ml.data_pipeline import DataPipeline

logger = logging.getLogger(__name__)

class GoalService:
    def __init__(self, db: Session):
        self.db = db
        self.predictor = GoalDifficultyPredictor()
        try:
            self.predictor.load_model()
        except FileNotFoundError:
            logger.warning("Model not found. Predictions will not work until trained.")

    def predict_goal(self, request: GoalRequest) -> GoalPredictionResponse:
        """Predicts goal attributes using the ML model."""
        # Simple feature extraction similar to what data_pipeline does
        goal_length = len(request.title) + len(request.description)
        
        # We instantiate pipeline just to use its complexity calculation
        pipeline = DataPipeline("dummy_path")
        complex_keywords = pipeline.complex_keywords
        
        complexity_score = sum(1 for w in complex_keywords if w in request.title.lower()) + \
                           sum(1 for w in complex_keywords if w in request.description.lower())
        
        # Mocking category code for now, in a real scenario we'd use a fitted encoder
        category_code = hash(request.category) % 10 
        
        difficulty = self.predictor.predict(goal_length, complexity_score, category_code)
        
        return GoalPredictionResponse(
            difficulty=difficulty,
            estimated_success_probability=75.5, # Mocked additional metrics
            estimated_completion_time_days=90
        )
        
    def generate_plan(self, request: GoalRequest) -> GoalPlanResponse:
        """Integration with LLM and DB will be fully implemented in Step 7."""
        # Placeholder for Step 6
        prediction = self.predict_goal(request)
        
        return GoalPlanResponse(
            goal_id=None,
            plan_data={"status": "Pending Step 7 Implementation"},
            metadata={"difficulty": prediction.difficulty}
        )
        
    def get_history(self):
        """Fetches goal history from the database."""
        # Implementation to be completed in Step 7
        return []
