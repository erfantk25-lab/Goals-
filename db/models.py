from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))

    goals = relationship("Goal", back_populates="owner")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), onupdate=text('CURRENT_TIMESTAMP'))

    owner = relationship("User", back_populates="goals")
    prediction = relationship("GoalPrediction", back_populates="goal", uselist=False)
    plan = relationship("GoalPlan", back_populates="goal", uselist=False)


class GoalPrediction(Base):
    __tablename__ = "goal_predictions"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), unique=True)
    difficulty = Column(String, nullable=False)
    estimated_success_probability = Column(Float, nullable=False)
    estimated_completion_time_days = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))

    goal = relationship("Goal", back_populates="prediction")


class GoalPlan(Base):
    __tablename__ = "goal_plans"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), unique=True)
    plan_data = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False) # Stores the 12 steps
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))

    goal = relationship("Goal", back_populates="plan")


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), index=True)
    metric_name = Column(String, index=True, nullable=False)
    metric_value = Column(Float, nullable=False)
    model_version = Column(String, nullable=False)


class LLMMetric(Base):
    __tablename__ = "llm_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), index=True)
    prompt_version_id = Column(String, nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    validation_success = Column(Boolean, nullable=False)
    category = Column(String, nullable=True)


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), index=True)
    request_id = Column(String, index=True, nullable=False)
    endpoint = Column(String, nullable=False)
    latency_ms = Column(Float, nullable=False)
    status_code = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    request_payload = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)


class DriftMetric(Base):
    __tablename__ = "drift_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), index=True)
    drift_score = Column(Float, nullable=False)
    drift_detected = Column(Boolean, nullable=False)
    method = Column(String, nullable=False)
    feature_name = Column(String, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), index=True)
    alert_type = Column(String, index=True, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(Text, nullable=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    goal_plan_id = Column(Integer, ForeignKey("goal_plans.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rating = Column(Integer, nullable=False) # e.g. 1-5
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    plan = relationship("GoalPlan")
    user = relationship("User")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    dataset_version = Column(String, nullable=True)
    hyperparameters = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    metrics = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    is_active = Column(Boolean, default=False)


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    template_text = Column(Text, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    model_version_id = Column(String, ForeignKey("model_versions.version_id"))
    evaluated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    confusion_matrix = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    
    model_version = relationship("ModelVersion")
