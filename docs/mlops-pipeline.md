# MLOps Pipeline Documentation

## Overview
The Goal Planner AI uses a full end-to-end Machine Learning Operations (MLOps) pipeline for continuous training, evaluation, and serving of the Goal Difficulty Prediction model.

## Directory Structure
The ML logic is strictly separated following Clean Architecture:
- `/ml/data`: Data ingestion, preprocessing, and feature engineering (`data_pipeline.py`).
- `/ml/training`: The core model training scripts, CV, and hyperparameter tuning (`train.py`).
- `/ml/evaluation`: Utility classes to calculate Accuracy, Precision, Recall, F1, and Confusion Matrices (`evaluator.py`).
- `/ml/registry`: The Model Registry handling database logging of model lineage, metrics, and parameters (`model_registry.py`).
- `/ml/models`: The artifact store where `*.joblib` files are saved.

## Model Registry
Instead of overwriting `model.joblib`, each training run now generates a unique Version ID (e.g., `v-a1b2c3d4`).
This version is persisted in the PostgreSQL `ModelVersions` table, including:
1. `version_id`: UUID
2. `dataset_version`: Version of the training data
3. `hyperparameters`: JSON payload of the model's parameters (e.g. `n_estimators`, `max_depth`)
4. `metrics`: Evaluated metrics during cross-validation
5. `is_active`: Boolean flag indicating if this model is the currently serving production model.

## Evaluation Results
The `EvaluationResults` table stores detailed classification metrics including Precision, Recall, F1-Score, and a JSON-serialized Confusion Matrix, linked via Foreign Key to the `ModelVersion`.

## Model Serving
When FastAPI boots, `train.py` (via `GoalDifficultyPredictor`) connects to the Model Registry, looks up the active `ModelVersion`, and loads the correct `.joblib` file from disk dynamically. This ensures zero downtime rollbacks are possible simply by flipping the `is_active` boolean in the database.
