# LLMOps Pipeline Documentation

## Overview
The Goal Planner AI uses an advanced Large Language Model Operations (LLMOps) layer to manage prompts, versioning, observability, and structured output parsing.

## Prompt Management & Versioning
Prompts are no longer static text strings hidden in code.
1. The `PromptManager` (`prompts/prompt_manager.py`) acts as the intermediary between the LLM Service and the prompt templates.
2. It dynamically fetches the `is_active` prompt from the `PromptVersions` PostgreSQL table.
3. If no prompt exists, it defaults to the local `.txt` file and automatically synchronizes it into the database for future tracking.
4. By querying the database, we can trace exactly which prompt version generated a specific plan, allowing A/B testing of prompt engineering.

## Guardrails
Large Language Models are probabilistic and prone to hallucinations or format deviations.
To protect the system, we implemented `LLMGuardrails` (`prompts/guardrails.py`):
- **JSON Validation**: Enforces that the output is strictly valid JSON.
- **Schema Validation**: Ensures the JSON contains a `steps` array with exactly 12 items.
- **Key Validation**: Loops through every step to ensure `step_number`, `title`, and `action` keys exist.
If the guardrails fail, the LLM integration can trigger a retry mechanism or alert the monitoring system.

## Continuous Improvement Feedback Loop
We expose a `POST /api/v1/feedback` endpoint. 
Users can submit a 1-5 rating and comments for any generated Goal Plan. This feedback is stored in the `Feedback` table, linked to the exact `GoalPlan` and `PromptVersion` used. Over time, data engineers can use this feedback to fine-tune the LLM or curate better prompt engineering techniques.
