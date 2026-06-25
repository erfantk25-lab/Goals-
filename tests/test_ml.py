from ml.model import GoalDifficultyPredictor

def test_model_loading_and_prediction():
    predictor = GoalDifficultyPredictor()
    predictor.load_model()
    
    # Passing raw numerical features that the model expects: 
    # goal_length, complexity_score, category_code
    prediction = predictor.predict(goal_length=80, complexity_score=3, category_code=1)
    
    # Validate the prediction falls within expected classes
    valid_classes = ["Easy", "Medium", "Hard"]
    assert prediction in valid_classes, f"Prediction {prediction} not in {valid_classes}"
