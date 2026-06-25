import logging
from sqlalchemy.orm import Session
from api.schemas import GoalRequest, GoalPredictionResponse, GoalPlanResponse, HistoryResponse
from ml.model import GoalDifficultyPredictor
from ml.data_pipeline import DataPipeline
from ml.llm_service import LLMService
from db.models import Goal, GoalPrediction, GoalPlan

logger = logging.getLogger(__name__)

class GoalService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.predictor = GoalDifficultyPredictor()
        try:
            self.predictor.load_model()
        except FileNotFoundError:
            logger.warning("Model not found. Predictions will not work until trained.")

    def predict_goal(self, request: GoalRequest) -> GoalPredictionResponse:
        """Predicts goal attributes using the ML model."""
        goal_length = len(request.title) + len(request.description)
        pipeline = DataPipeline("dummy_path")
        complex_keywords = pipeline.complex_keywords
        
        complexity_score = sum(1 for w in complex_keywords if w in request.title.lower()) + \
                           sum(1 for w in complex_keywords if w in request.description.lower())
        
        category_code = hash(request.category) % 10 
        difficulty = self.predictor.predict(goal_length, complexity_score, category_code)
        
        return GoalPredictionResponse(
            difficulty=difficulty,
            estimated_success_probability=75.5,
            estimated_completion_time_days=90
        )
        
    def generate_plan(self, request: GoalRequest) -> GoalPlanResponse:
        """Integration Flow: ML Prediction -> LLM Generation -> DB Storage"""
        
        # 1. ML Prediction
        prediction = self.predict_goal(request)
        
        # 2. LLM Plan Generation
        llm_output = self.llm_service.generate_12_step_plan(
            goal=request.title,
            category=request.category,
            difficulty=prediction.difficulty,
            estimated_success=prediction.estimated_success_probability
        )
        
        # 3. DB Storage Transaction
        try:
            # Create Goal
            db_goal = Goal(
                title=request.title,
                description=request.description,
                category=request.category
            )
            self.db.add(db_goal)
            self.db.flush() # Get goal ID without committing
            
            # Create Prediction
            db_pred = GoalPrediction(
                goal_id=db_goal.id,
                difficulty=prediction.difficulty,
                estimated_success_probability=prediction.estimated_success_probability,
                estimated_completion_time_days=prediction.estimated_completion_time_days
            )
            self.db.add(db_pred)
            
            # Create Plan
            db_plan = GoalPlan(
                goal_id=db_goal.id,
                plan_data=llm_output["goal_plan"]
            )
            self.db.add(db_plan)
            
            # Commit the entire transaction
            self.db.commit()
            logger.info(f"Successfully generated and saved plan for goal ID: {db_goal.id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise e

        # 4. Return API Response
        return GoalPlanResponse(
            goal_id=db_goal.id,
            plan_data=llm_output["goal_plan"],
            metadata=llm_output["metadata"]
        )
        
    def get_history(self) -> list[HistoryResponse]:
        """Fetches goal history from the database."""
        goals = self.db.query(Goal).order_by(Goal.created_at.desc()).all()
        return [
            HistoryResponse(
                id=g.id,
                title=g.title,
                category=g.category,
                created_at=g.created_at
            ) for g in goals
        ]
