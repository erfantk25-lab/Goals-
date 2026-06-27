from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Goal Planner System"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "goal_planner"
    POSTGRES_PORT: str = "5432"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        import os
        if os.getenv("TESTING") == "1":
            return "sqlite:///test.db"
        
        # Local development fallback
        if os.getenv("ENVIRONMENT") != "production":
            return "sqlite:///goal_planner.db"
            
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # ML Model Settings
    MODEL_PATH: str = "ml/models/model.joblib"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
