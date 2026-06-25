import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)

    def load_prompt(self, version: str = "v1") -> str:
        """Loads a specific version of the prompt."""
        prompt_path = self.prompts_dir / f"{version}.txt"
        
        if not prompt_path.exists():
            logger.error(f"Prompt version {version} not found.")
            raise FileNotFoundError(f"Prompt file {prompt_path} does not exist.")
            
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
            
        return prompt_content
        
    def generate_messages(self, goal: str, category: str, difficulty: str, estimated_success: float, version: str = "v1") -> list:
        """Formats the prompt with user variables for use in an LLM API."""
        prompt_template = self.load_prompt(version)
        
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

# Example usage
if __name__ == "__main__":
    pm = PromptManager()
    msgs = pm.generate_messages(
        goal="Launch a new SaaS product",
        category="Business",
        difficulty="Hard",
        estimated_success=65.5
    )
    print("Messages successfully formatted for API consumption.")
