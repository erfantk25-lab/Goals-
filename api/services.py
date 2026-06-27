import logging
from sqlalchemy.orm import Session
from api.schemas import GoalRequest, GoalPredictionResponse, GoalPlanResponse, HistoryResponse
from ml.training.train import GoalDifficultyPredictor
from ml.data.data_pipeline import DataPipeline
from ml.llm_service import LLMService
from db.models import Goal, GoalPrediction, GoalPlan
from api.repositories.goal_repository import goal_repo

from monitoring.drift.data_drift import check_data_drift
from monitoring.drift.concept_drift import ConceptDriftTracker
from monitoring.metrics.daos import save_model_metric, save_llm_metric, save_drift_metric
from monitoring.alerts.alert_manager import AlertManager

logger = logging.getLogger(__name__)

# Global instances for tracking
drift_tracker = ConceptDriftTracker()
BASELINE_GOAL_LENGTHS = [15, 25, 30, 40, 50, 60, 70, 80, 90, 100, 120]
live_goal_lengths = []

class GoalService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.predictor = GoalDifficultyPredictor()
        self.alert_manager = AlertManager(self.db)
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
        
        # --- MONITORING: Data Drift ---
        live_goal_lengths.append(goal_length)
        if len(live_goal_lengths) > 50:
            live_goal_lengths.pop(0)
            
        drift_result = check_data_drift(BASELINE_GOAL_LENGTHS, live_goal_lengths, "goal_length")
        save_drift_metric(
            self.db, 
            drift_score=drift_result["drift_score"], 
            drift_detected=drift_result["drift_detected"], 
            method=drift_result["method"], 
            feature_name=drift_result["feature_name"]
        )
        self.alert_manager.check_drift_alert(drift_result["drift_score"], drift_result["method"])

        # --- MONITORING: Concept Drift & Model Metrics ---
        # Log basic model metric
        save_model_metric(self.db, "complexity_score", complexity_score, "v1.0")
        
        # Simulate tracking
        drift_tracker.add_prediction(difficulty)
        accuracy = drift_tracker.calculate_rolling_accuracy()
        save_model_metric(self.db, "rolling_accuracy", accuracy, "v1.0")
        
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
            estimated_success=prediction.estimated_success_probability,
            use_rag=getattr(request, 'use_rag', False)
        )
        
        # --- MONITORING: LLM Metrics ---
        metrics = llm_output.get("monitoring_metrics", {})
        if metrics:
            save_llm_metric(
                self.db,
                prompt_version_id=metrics["prompt_version_id"],
                input_tokens=metrics["input_tokens"],
                output_tokens=metrics["output_tokens"],
                latency_ms=metrics["latency_ms"],
                validation_success=metrics["validation_success"],
                category=request.category
            )
            # Simulate failure check randomly
            self.alert_manager.check_llm_validation_alert(total_llm_calls=20, failed_calls=1 if not metrics["validation_success"] else 0)

        # 3. DB Storage Transaction
        try:
            db_plan = goal_repo.create_goal_with_prediction_and_plan(
                db=self.db,
                title=request.title,
                description=request.description,
                category=request.category,
                difficulty=prediction.difficulty,
                est_success=prediction.estimated_success_probability,
                est_time=prediction.estimated_completion_time_days,
                plan_data=llm_output["goal_plan"]
            )
            logger.info(f"Successfully generated and saved plan for goal ID: {db_plan.goal_id}")
        except Exception as e:
            logger.error(f"Database transaction failed: {e}")
            raise e

        # 4. Return API Response
        return GoalPlanResponse(
            goal_id=db_plan.goal_id,
            plan_data=llm_output["goal_plan"],
            metadata=llm_output["metadata"]
        )

    def update_plan(self, goal_id: int, plan_data: dict) -> GoalPlanResponse:
        db_plan = goal_repo.update_plan_data(self.db, goal_id, plan_data)
        if not db_plan:
            raise ValueError("Plan not found")
        return GoalPlanResponse(
            goal_id=db_plan.goal_id,
            plan_data=db_plan.plan_data,
            metadata={}
        )

    def replan(self, goal_id: int, failed_step_number: int, all_steps: list) -> GoalPlanResponse:
        """Re-generates remaining steps after a user fails a specific step."""
        completed_steps = [s for s in all_steps if s.get('step_number', 0) < failed_step_number]
        failed_step = next((s for s in all_steps if s.get('step_number') == failed_step_number), {})
        remaining_steps = [s for s in all_steps if s.get('step_number', 0) > failed_step_number]

        new_steps = self.llm_service.generate_replan(
            goal="",
            category="",
            failed_step_title=failed_step.get('title', 'Unknown Step'),
            failed_step_action=failed_step.get('action', ''),
            completed_steps=completed_steps,
            remaining_steps=remaining_steps
        )

        # Reconstruct the full plan with original completed + failed + new remaining
        failed_step_updated = dict(failed_step)
        failed_step_updated['is_failed'] = True
        full_steps = completed_steps + [failed_step_updated] + new_steps
        new_plan_data = {"steps": full_steps}

        db_plan = goal_repo.update_plan_data(self.db, goal_id, new_plan_data)
        if not db_plan:
            raise ValueError("Plan not found")
        return GoalPlanResponse(
            goal_id=db_plan.goal_id,
            plan_data=db_plan.plan_data,
            metadata={"replanned": True, "failed_step": failed_step_number}
        )
        
    def get_history(self) -> list[HistoryResponse]:
        goals = goal_repo.get_all_goals_desc(self.db)
        return [
            HistoryResponse(
                id=g.id,
                title=g.title,
                category=g.category,
                created_at=g.created_at
            ) for g in goals
        ]

    def ask_ai(self, step_title: str, step_action: str, question: str) -> str:
        return self.llm_service.ask_step_question(step_title, step_action, question)

    def delete_goal(self, goal_id: int):
        deleted = goal_repo.delete_goal(self.db, goal_id)
        if not deleted:
            raise ValueError(f"Goal {goal_id} not found")
