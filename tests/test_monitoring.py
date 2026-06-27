import numpy as np
import pytest
from monitoring.drift.data_drift import calculate_psi, check_data_drift
from monitoring.drift.concept_drift import ConceptDriftTracker

def test_calculate_psi_no_drift():
    # Same distribution
    expected = np.random.normal(50, 10, 1000)
    actual = np.random.normal(50, 10, 1000)
    psi = calculate_psi(expected, actual)
    assert psi < 0.1

def test_calculate_psi_with_drift():
    # Different distribution
    expected = np.random.normal(50, 10, 1000)
    actual = np.random.normal(100, 10, 1000)
    psi = calculate_psi(expected, actual)
    assert psi > 0.2

def test_check_data_drift():
    expected = [50] * 100
    actual = [100] * 100
    result = check_data_drift(expected, actual, "length")
    assert result["drift_detected"] is True
    assert result["drift_score"] > 0.2
    assert result["method"] == "PSI"

def test_concept_drift_tracker():
    tracker = ConceptDriftTracker(window_size=5)
    
    tracker.add_prediction("Hard", "Hard")
    tracker.add_prediction("Medium", "Medium")
    tracker.add_prediction("Easy", "Easy")
    assert tracker.calculate_rolling_accuracy() == 1.0
    
    tracker.add_prediction("Hard", "Easy")
    tracker.add_prediction("Hard", "Easy")
    assert tracker.calculate_rolling_accuracy() == 0.6  # 3/5
    
    # Push out old correct predictions
    tracker.add_prediction("Hard", "Easy")
    tracker.add_prediction("Hard", "Easy")
    tracker.add_prediction("Hard", "Easy")
    assert tracker.calculate_rolling_accuracy() == 0.0  # 0/5
