import numpy as np
from typing import Dict, Any, Tuple

def calculate_psi(expected: np.ndarray, actual: np.ndarray, buckets: int = 10) -> float:
    """
    Calculate the Population Stability Index (PSI) between two distributions.
    A PSI < 0.1 means no significant change.
    A PSI between 0.1 and 0.2 means moderate change.
    A PSI > 0.2 means significant change.
    """
    def scale_range(input_data, min_val, max_val):
        if max_val == min_val:
            return input_data * 0 + min_val
        input_data += -(np.min(input_data))
        input_data /= np.max(input_data) / (max_val - min_val)
        input_data += min_val
        return input_data

    breakpoints = np.arange(0, buckets + 1) / (buckets) * 100
    breakpoints = scale_range(breakpoints, np.min(expected), np.max(expected))
    
    expected_fractions = np.histogram(expected, breakpoints)[0] / len(expected)
    actual_fractions = np.histogram(actual, breakpoints)[0] / len(actual)
    
    # Replace 0s to avoid division by zero
    expected_fractions = np.where(expected_fractions == 0, 0.0001, expected_fractions)
    actual_fractions = np.where(actual_fractions == 0, 0.0001, actual_fractions)
    
    psi_values = (expected_fractions - actual_fractions) * np.log(expected_fractions / actual_fractions)
    psi = np.sum(psi_values)
    
    return float(psi)

def check_data_drift(expected_data: list, actual_data: list, feature_name: str, threshold: float = 0.2) -> Dict[str, Any]:
    if not expected_data or not actual_data:
        return {
            "drift_score": 0.0,
            "drift_detected": False,
            "method": "PSI",
            "feature_name": feature_name,
            "error": "Insufficient data"
        }
        
    psi_score = calculate_psi(np.array(expected_data), np.array(actual_data))
    
    return {
        "drift_score": round(psi_score, 4),
        "drift_detected": psi_score > threshold,
        "method": "PSI",
        "feature_name": feature_name
    }
