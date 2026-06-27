from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import numpy as np
from sqlalchemy.orm import Session
from db.models import EvaluationResult

class ModelEvaluator:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_and_save(self, model_version_id: str, y_true: np.ndarray, y_pred: np.ndarray) -> EvaluationResult:
        """Calculates classification metrics and saves them to the DB."""
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_true, y_pred).tolist()

        result = EvaluationResult(
            model_version_id=model_version_id,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            confusion_matrix=cm
        )
        
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        
        return result

    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """Returns metrics as a dictionary (used for ModelVersion metrics)."""
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y_true, y_pred, average='weighted', zero_division=0),
            "f1_score": f1_score(y_true, y_pred, average='weighted', zero_division=0)
        }
