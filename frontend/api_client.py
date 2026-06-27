import requests
import json
from typing import Dict, Any, List

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

class APIClient:
    """Client for communicating with the Goal Planner AI FastAPI backend."""
    
    @staticmethod
    def generate_goal_plan(title: str, description: str, category: str, use_rag: bool = False) -> Dict[str, Any]:
        """Generates a 12-step plan using the backend LLM service."""
        payload = {
            "title": title,
            "description": description,
            "category": category,
            "use_rag": use_rag
        }
        
        response = requests.post(f"{API_BASE_URL}/generate-goal-plan", json=payload)
        response.raise_for_status()
        return response.json()
        
    @staticmethod
    def update_goal_plan(goal_id: int, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the completion status of the plan steps."""
        payload = {"plan_data": plan_data}
        response = requests.put(f"{API_BASE_URL}/plan/{goal_id}", json=payload)
        response.raise_for_status()
        return response.json()
        
    @staticmethod
    def ask_ai(step_title: str, step_action: str, question: str) -> str:
        """Asks the AI a question about a specific step."""
        payload = {
            "step_title": step_title,
            "step_action": step_action,
            "question": question
        }
        response = requests.post(f"{API_BASE_URL}/ask-ai", json=payload)
        response.raise_for_status()
        return response.json().get("answer", "No answer received.")
        
    @staticmethod
    def submit_feedback(goal_plan_id: int, rating: int, comments: str = "") -> Dict[str, Any]:
        """Submits feedback for a generated goal plan."""
        payload = {
            "goal_plan_id": goal_plan_id,
            "rating": rating,
            "comments": comments
        }
        
        response = requests.post(f"{API_BASE_URL}/feedback/", json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_history() -> List[Dict[str, Any]]:
        """Fetches the history of previously generated goals."""
        response = requests.get(f"{API_BASE_URL}/history")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Fetches MLOps and LLMOps metrics for the dashboard."""
        response = requests.get(f"{API_BASE_URL}/dashboard-metrics")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def replan_goal(goal_id: int, failed_step_number: int, all_steps: list) -> Dict[str, Any]:
        """Triggers a dynamic re-plan after a user fails a step."""
        payload = {
            "failed_step_number": failed_step_number,
            "steps": all_steps
        }
        response = requests.post(f"{API_BASE_URL}/plan/{goal_id}/replan", json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def trigger_retrain() -> Dict[str, Any]:
        """Triggers a live ML model retraining job."""
        response = requests.post(f"{API_BASE_URL}/mlops/retrain")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_metrics_history() -> Dict[str, Any]:
        """Fetches time-series data for dashboard charts."""
        response = requests.get(f"{API_BASE_URL}/metrics-history")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_feedback_summary() -> Dict[str, Any]:
        """Fetches aggregated feedback ratings."""
        response = requests.get(f"{API_BASE_URL}/feedback-summary")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def delete_goal(goal_id: int) -> Dict[str, Any]:
        """Deletes a goal and all its related data."""
        response = requests.delete(f"{API_BASE_URL}/goal/{goal_id}")
        response.raise_for_status()
        return response.json()
