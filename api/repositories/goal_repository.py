from typing import List
from sqlalchemy.orm import Session
from api.repositories.base import BaseRepository
from db.models import Goal, GoalPrediction, GoalPlan

class GoalRepository(BaseRepository[Goal]):
    def __init__(self):
        super().__init__(Goal)

    def get_all_goals_desc(self, db: Session) -> List[Goal]:
        return db.query(self.model).order_by(self.model.created_at.desc()).all()

    def create_goal_with_prediction_and_plan(self, db: Session, title: str, description: str, category: str, difficulty: str, est_success: float, est_time: int, plan_data: dict) -> GoalPlan:
        try:
            db_goal = Goal(title=title, description=description, category=category)
            db.add(db_goal)
            db.flush()
            
            db_pred = GoalPrediction(
                goal_id=db_goal.id,
                difficulty=difficulty,
                estimated_success_probability=est_success,
                estimated_completion_time_days=est_time
            )
            db.add(db_pred)
            
            db_plan = GoalPlan(
                goal_id=db_goal.id,
                plan_data=plan_data
            )
            db.add(db_plan)
            
            db.commit()
            return db_plan
        except Exception as e:
            db.rollback()
            raise e

    def update_plan_data(self, db: Session, goal_id: int, plan_data: dict) -> GoalPlan:
        db_plan = db.query(GoalPlan).filter(GoalPlan.goal_id == goal_id).first()
        if db_plan:
            db_plan.plan_data = plan_data
            db.commit()
            db.refresh(db_plan)
        return db_plan

    def delete_goal(self, db: Session, goal_id: int) -> bool:
        """Deletes a goal and all its related records."""
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return False
        # Cascade delete related records
        db.query(GoalPlan).filter(GoalPlan.goal_id == goal_id).delete()
        db.query(GoalPrediction).filter(GoalPrediction.goal_id == goal_id).delete()
        db.delete(goal)
        db.commit()
        return True

goal_repo = GoalRepository()
