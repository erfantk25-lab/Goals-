import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from db.models import ModelVersion

class ModelRegistry:
    def __init__(self, db: Session):
        self.db = db

    def register_model(self, dataset_version: str, hyperparameters: Dict[str, Any], metrics: Dict[str, Any]) -> ModelVersion:
        """Registers a new model version in the database."""
        # Deactivate all currently active models
        self.db.query(ModelVersion).filter(ModelVersion.is_active == True).update({"is_active": False})
        
        # Create new model version
        version_id = f"v-{uuid.uuid4().hex[:8]}"
        new_version = ModelVersion(
            version_id=version_id,
            dataset_version=dataset_version,
            hyperparameters=hyperparameters,
            metrics=metrics,
            is_active=True
        )
        
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        return new_version

    def get_latest_production_model(self) -> Optional[ModelVersion]:
        """Fetches the currently active model version."""
        return self.db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
