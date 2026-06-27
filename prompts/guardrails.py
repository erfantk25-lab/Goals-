import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LLMGuardrails:
    """Provides validation and parsing guardrails for LLM responses."""
    
    @staticmethod
    def validate_12_step_schema(output: str) -> Dict[str, Any]:
        """Validates that the LLM output is a valid JSON with exactly 12 steps."""
        try:
            parsed = json.loads(output)
            
            if "steps" not in parsed:
                raise ValueError("Output missing 'steps' key.")
                
            steps = parsed["steps"]
            if not isinstance(steps, list):
                raise ValueError("'steps' must be a list.")
                
            if len(steps) != 12:
                raise ValueError(f"Expected exactly 12 steps, got {len(steps)}.")
                
            for i, step in enumerate(steps):
                if "step_number" not in step or "title" not in step or "action" not in step:
                    raise ValueError(f"Step {i+1} is missing required keys (step_number, title, action).")
                    
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM output as JSON: {e}")
            raise ValueError("LLM output is not valid JSON.") from e
