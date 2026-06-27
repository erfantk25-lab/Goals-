import os
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from db.models import PromptVersion
from db.session import SessionLocal

logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)

    def load_prompt(self, db: Session, version: str = "v1") -> str:
        """Loads a specific version of the prompt from DB or fallback to file."""
        # Check DB first for active prompt if version is 'latest'
        if version == "latest":
            db_prompt = db.query(PromptVersion).filter(PromptVersion.is_active == True).first()
            if db_prompt:
                return db_prompt.template_text
            version = "v1" # Fallback to v1

        prompt_path = self.prompts_dir / f"{version}.txt"
        
        if not prompt_path.exists():
            logger.error(f"Prompt version {version} not found.")
            raise FileNotFoundError(f"Prompt file {prompt_path} does not exist.")
            
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
            
        # Automatically sync file prompt to DB if it doesn't exist
        existing = db.query(PromptVersion).filter(PromptVersion.version_id == version).first()
        if not existing:
            new_prompt = PromptVersion(
                version_id=version,
                template_text=prompt_content,
                is_active=True
            )
            db.add(new_prompt)
            db.commit()
            
        return prompt_content
        
    def generate_messages(self, goal: str, category: str, difficulty: str, estimated_success: float, version: str = "latest", db: Session = None) -> list:
        """Formats the prompt with user variables for use in an LLM API."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
            
        try:
            prompt_template = self.load_prompt(db, version)
            
            formatted_prompt = prompt_template.format(
                goal=goal,
                category=category,
                difficulty=difficulty,
                estimated_success=estimated_success
            )
            
            # Structure ready for OpenAI or similar Chat APIs
            return [
                {"role": "system", "content": "You are an API that outputs strictly valid JSON without markdown wrapping."},
                {"role": "user", "content": formatted_prompt}
            ]
        finally:
            if should_close:
                db.close()
