# System Architecture

## Overview
The AI Goal Planner System is a production-ready MLOps platform that combines predictive Machine Learning with Generative AI to provide users with highly structured, actionable 12-step goal execution plans based on the Brian Tracy methodology.

## High-Level Flow
1. **Client Request**: The client sends a `POST /api/v1/generate-goal-plan` request with the user's goal title, description, and category.
2. **FastAPI Controller**: The request is validated against strict Pydantic schemas.
3. **Service Layer (`api/services.py`)**:
   - **ML Prediction**: The raw text is passed to the `DataPipeline` for feature extraction (length, complexity score) and then sent to the pre-trained `RandomForestClassifier` (`GoalDifficultyPredictor`) to assess the goal's difficulty.
   - **LLM Generation**: The calculated difficulty and user intent are fed into the `PromptManager`, which constructs a version-controlled prompt (`prompts/v1.txt`). The `LLMService` interacts with the LLM API (or a deterministic fallback mock) to produce a strict JSON output matching the 12-step methodology.
4. **Database Storage**: Using an atomic SQLAlchemy transaction, the original Goal, the ML Prediction, and the generated JSON Plan are saved to PostgreSQL.

## Core Components
- **API (FastAPI)**: Handles routing, validation, and HTTP responses.
- **ML Pipeline (Scikit-Learn/Pandas)**: Handles data extraction, feature engineering, and model inference.
- **LLM Service**: Abstracts prompt formatting and API integrations to prevent vendor lock-in.
- **PostgreSQL Database**: Uses native `JSONB` for unstructured plan storage and relational tables for predictions and goals.
- **Docker**: Containerizes the API and Database to ensure identical environments across staging and production.
