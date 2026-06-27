import os
import joblib
import logging
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
import sys

# Ensure project root is in python path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ml.data.data_pipeline import DataPipeline
from ml.registry.model_registry import ModelRegistry
from ml.evaluation.evaluator import ModelEvaluator
from db.session import SessionLocal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoalDifficultyPredictor:
    def __init__(self, model_dir="ml/models"):
        self.model_dir = model_dir
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.model_path = None
        
    def train(self, data_path="ml/data/raw/goals_dataset.csv"):
        logger.info("Loading and preprocessing data...")
        pipeline = DataPipeline(data_path)
        df = pipeline.preprocess_data()
        
        X = df[['goal_length', 'complexity_score', 'category_code']]
        y = df['difficulty']
        
        logger.info("Splitting dataset...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        logger.info("Performing 5-Fold Cross-Validation...")
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring='accuracy')
        logger.info(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        logger.info("Training final model on full training set...")
        self.model.fit(X_train, y_train)
        
        logger.info("Evaluating on test set...")
        preds = self.model.predict(X_test)
        
        # Connect to DB for Registry and Evaluator
        db = SessionLocal()
        try:
            evaluator = ModelEvaluator(db)
            registry = ModelRegistry(db)
            
            metrics = evaluator.calculate_metrics(y_test, preds)
            logger.info(f"Test Metrics: {metrics}")
            
            hyperparams = self.model.get_params()
            
            # Register Model
            version = registry.register_model(
                dataset_version="v1.0",
                hyperparameters=hyperparams,
                metrics=metrics
            )
            logger.info(f"Registered new model version: {version.version_id}")
            
            # Save evaluation results
            evaluator.evaluate_and_save(version.version_id, y_test, preds)
            
            # Save artifact
            self.model_path = os.path.join(self.model_dir, f"{version.version_id}.joblib")
            os.makedirs(self.model_dir, exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
            
        finally:
            db.close()
            
    def load_model(self):
        db = SessionLocal()
        try:
            registry = ModelRegistry(db)
            latest = registry.get_latest_production_model()
            if not latest:
                # Fallback to default if no registry entry
                self.model_path = os.path.join(self.model_dir, "model.joblib")
            else:
                self.model_path = os.path.join(self.model_dir, f"{latest.version_id}.joblib")
                
            if not os.path.exists(self.model_path):
                # Fallback
                self.model_path = os.path.join(self.model_dir, "model.joblib")
                if not os.path.exists(self.model_path):
                    raise FileNotFoundError(f"Model not found at {self.model_path}")
                    
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded successfully from {self.model_path}")
        finally:
            db.close()
        
    def predict(self, goal_length, complexity_score, category_code):
        """Predicts the difficulty of a given goal."""
        return self.model.predict([[goal_length, complexity_score, category_code]])[0]

if __name__ == "__main__":
    predictor = GoalDifficultyPredictor()
    predictor.train()
