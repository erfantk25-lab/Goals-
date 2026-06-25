import os
import joblib
import logging
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import sys

# Ensure project root is in python path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.data_pipeline import DataPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoalDifficultyPredictor:
    def __init__(self, model_path="ml/models/model.joblib"):
        self.model_path = model_path
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        
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
        logger.info(f"Test Accuracy: {accuracy_score(y_test, preds):.4f}")
        logger.info(f"\nClassification Report:\n{classification_report(y_test, preds)}")
        
        self.save_model()
        
    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
        
    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        self.model = joblib.load(self.model_path)
        logger.info(f"Model loaded successfully from {self.model_path}")
        
    def predict(self, goal_length, complexity_score, category_code):
        """Predicts the difficulty of a given goal."""
        return self.model.predict([[goal_length, complexity_score, category_code]])[0]

if __name__ == "__main__":
    predictor = GoalDifficultyPredictor()
    predictor.train()
