from typing import List

class ConceptDriftTracker:
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.predictions = []
        self.ground_truths = []
        
    def add_prediction(self, prediction: str, ground_truth: str = None):
        """Simulates recording a prediction and its true value if known."""
        self.predictions.append(prediction)
        if ground_truth is not None:
            self.ground_truths.append(ground_truth)
            
        # Keep window size
        if len(self.predictions) > self.window_size:
            self.predictions.pop(0)
        if len(self.ground_truths) > self.window_size:
            self.ground_truths.pop(0)
            
    def calculate_rolling_accuracy(self) -> float:
        """Calculates accuracy over the recent window."""
        if not self.ground_truths:
            return 1.0 # Default if no ground truth available
            
        correct = sum(1 for p, g in zip(self.predictions[-len(self.ground_truths):], self.ground_truths) if p == g)
        return float(correct) / len(self.ground_truths)
