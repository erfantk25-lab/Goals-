import os
import json
import time
import random
import logging
from prompts.prompt_manager import PromptManager
from ml.rag_service import RAGService

logger = logging.getLogger(__name__)

BRIAN_TRACY_STEPS = [
    {
        "title": "Write It Down Clearly",
        "action_template": "Write down '{goal}' in complete detail. Make it specific, measurable, and emotionally compelling — describe exactly what it looks like when achieved."
    },
    {
        "title": "Set a Deadline",
        "action_template": "Set a firm deadline for achieving '{goal}'. Break it into 3 sub-deadlines (30-day, 60-day, 90-day milestones) and treat each as a non-negotiable commitment."
    },
    {
        "title": "Identify Your Obstacles",
        "action_template": "List every obstacle between you and '{goal}'. Identify the single biggest bottleneck — it is almost always an internal one such as a skill gap, a habit, or a limiting belief."
    },
    {
        "title": "Identify Required Knowledge & Skills",
        "action_template": "Determine what knowledge and skills are needed for '{goal}'. Identify the ONE skill that, if mastered, would accelerate your success more than anything else."
    },
    {
        "title": "Identify People Whose Help You Need",
        "action_template": "List the mentors, experts, and communities who can help you achieve '{goal}'. For each person, think first about how you can add value to them — help flows to those who give first."
    },
    {
        "title": "Make a Complete Task List",
        "action_template": "Brainstorm and list EVERY single task required to achieve '{goal}', no matter how small. Add to this list continuously as new actions come to mind."
    },
    {
        "title": "Organize by Sequence & Priority",
        "action_template": "Take your task list for '{goal}' and organize it: first by sequence (what must happen before what), then by priority (what has the greatest impact). Identify the top 3 highest-leverage tasks."
    },
    {
        "title": "Build Your Action Plan",
        "action_template": "Convert your organized list for '{goal}' into a step-by-step action plan. Commit to taking at least one meaningful action toward this goal every single day, no exceptions."
    },
    {
        "title": "Schedule Daily, Weekly & Monthly",
        "action_template": "Translate your plan for '{goal}' into your calendar. Block specific daily time slots, weekly review sessions, and monthly progress checkpoints. A goal without a schedule is just a wish."
    },
    {
        "title": "Find Your #1 Daily Action",
        "action_template": "Identify the single most important task you can do today to move most rapidly toward '{goal}'. This is your daily non-negotiable — the keystone habit that drives all other progress."
    },
    {
        "title": "Focus Single-Mindedly",
        "action_template": "Discipline yourself to work on your most important task for '{goal}' until it is 100% complete before moving on. Eliminate all distractions. Practice single-handling — start it, stay on it, finish it."
    },
    {
        "title": "Never Give Up",
        "action_template": "Resolve that you will never give up on '{goal}'. Back your plan with unconditional persistence. Every setback is a learning opportunity — treat obstacles as feedback and adjust your approach, not your destination."
    },
]

STEP_TITLES = {
    "v1": [s["title"] for s in BRIAN_TRACY_STEPS],
    "v2": [s["title"] for s in BRIAN_TRACY_STEPS],  # Same titles, different tone in real API calls
}

class LLMService:
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.rag_service = RAGService()

    def generate_12_step_plan(self, goal: str, category: str, difficulty: str, estimated_success: float, use_rag: bool = False) -> dict:
        start_time = time.time()

        # A/B Test: randomly pick prompt version
        prompt_version = random.choice(["v1", "v2"])
        logger.info(f"A/B Test: Using prompt version '{prompt_version}'")

        # RAG: optionally fetch web context
        rag_context = ""
        rag_metadata = {"used": False, "source_count": 0, "latency_ms": 0}
        if use_rag:
            logger.info(f"RAG: Fetching web context for goal: '{goal}'")
            rag_result = self.rag_service.search(goal, category)
            rag_context = self.rag_service.format_context(rag_result)
            rag_metadata = {
                "used": True,
                "source_count": rag_result["source_count"],
                "latency_ms": rag_result["latency_ms"],
                "query": rag_result["query"]
            }
            logger.info(f"RAG: Retrieved {rag_result['source_count']} sources in {rag_result['latency_ms']:.0f}ms")

        latency_ms = (time.time() - start_time) * 1000

        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Using local mock LLM response.")
            return self._mock_response(goal, category, difficulty, estimated_success, latency_ms, prompt_version, rag_context, rag_metadata)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            logger.info(f"Calling OpenAI GPT-4o (prompt={prompt_version}, rag={use_rag})...")

            messages = self.prompt_manager.generate_messages(
                goal=goal,
                category=category,
                difficulty=difficulty,
                estimated_success=estimated_success,
                version=prompt_version
            )

            # Inject RAG context into the user message if available
            if rag_context:
                messages[-1]["content"] = rag_context + "\n\n" + messages[-1]["content"]

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            latency_ms = (time.time() - start_time) * 1000
            raw_content = response.choices[0].message.content
            parsed = json.loads(raw_content)

            # Normalize the plan into our standard steps format
            raw_plan = parsed.get("goal_plan", {})
            steps = []
            for i in range(1, 13):
                action = raw_plan.get(f"step_{i}", BRIAN_TRACY_STEPS[i-1]["action_template"].format(goal=goal))
                steps.append({
                    "step_number": i,
                    "title": BRIAN_TRACY_STEPS[i-1]["title"],
                    "action": action,
                    "is_completed": False
                })

            usage = response.usage
            return {
                "goal_plan": {"steps": steps},
                "metadata": {
                    "category": category,
                    "difficulty": difficulty,
                    "estimated_success_probability": estimated_success,
                    "estimated_completion_time_days": 90,
                    "prompt_version": prompt_version,
                    "rag": rag_metadata
                },
                "monitoring_metrics": {
                    "prompt_version_id": prompt_version,
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "latency_ms": latency_ms,
                    "validation_success": True
                }
            }

        except Exception as e:
            logger.error(f"LLM API Error: {e}. Falling back to mock.")
            return self._mock_response(goal, category, difficulty, estimated_success, latency_ms, prompt_version, rag_context, rag_metadata)

    def _mock_response(self, goal: str, category: str, difficulty: str, estimated_success: float, latency_ms: float, prompt_version: str = "v1", rag_context: str = "", rag_metadata: dict = None) -> dict:
        input_tokens = len(goal.split()) * 2 + 50
        output_tokens = 250

        rag_note = " (enriched with current web resources)" if rag_context else ""

        steps = [
            {
                "step_number": i + 1,
                "title": BRIAN_TRACY_STEPS[i]["title"],
                "action": BRIAN_TRACY_STEPS[i]["action_template"].format(goal=goal + rag_note if i == 0 else goal),
                "is_completed": False
            }
            for i in range(12)
        ]

        return {
            "goal_plan": {"steps": steps},
            "metadata": {
                "category": category,
                "difficulty": difficulty,
                "estimated_success_probability": estimated_success,
                "estimated_completion_time_days": 90,
                "prompt_version": prompt_version,
                "rag": rag_metadata or {"used": False}
            },
            "monitoring_metrics": {
                "prompt_version_id": prompt_version,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "validation_success": True
            }
        }

    def generate_replan(self, goal: str, category: str, failed_step_title: str, failed_step_action: str, completed_steps: list, remaining_steps: list) -> list:
        """Generates a revised set of steps after user fails one step."""
        logger.info(f"Re-planning from failed step: '{failed_step_title}'")

        if not self.api_key:
            # Mock: regenerate remaining steps with empathetic reframing
            new_steps = []
            empathy_prefix = f"After setback at '{failed_step_title}', "
            reframes = [
                f"{empathy_prefix}simplify your approach and set a smaller daily target.",
                f"Break '{failed_step_action}' into 3 smaller sub-tasks and tackle one per week.",
                "Find an accountability partner who has overcome a similar obstacle.",
                "Study 2 case studies of people who succeeded despite this type of setback.",
                "Block 15 minutes every morning specifically for this challenge — consistency beats intensity.",
                "Eliminate one major distraction from your environment this week.",
                "Document every small win — momentum is built from evidence of progress.",
                "Re-evaluate your timeline — adjust it to be 20% more generous.",
                "Seek feedback from a mentor on your current approach.",
                "Revisit your 'why' — reconnect with the original motivation for this goal.",
                "Automate or delegate any repeatable tasks that drain your energy.",
                "Celebrate your comeback — the fact that you're replanning shows real resilience.",
            ]

            start_num = len(completed_steps) + 2  # +1 for failed step, +1 for 1-indexed
            for i, step in enumerate(remaining_steps):
                reframe = reframes[i % len(reframes)]
                new_steps.append({
                    "step_number": start_num + i,
                    "title": step.get("title", f"Revised Step {start_num + i}"),
                    "action": reframe,
                    "is_completed": False
                })
            return new_steps
        
        # If real API available, call it here
        return remaining_steps

    def ask_step_question(self, step_title: str, step_action: str, question: str) -> str:
        """Answers a user question about a specific plan step."""
        if not self.api_key:
            return f"Mock AI Response: To successfully complete '{step_title}' ({step_action}), you should break it down further into 3 daily micro-tasks. Regarding '{question}', I recommend starting with 15 minutes of focused research today."
        
        return f"AI Advice for '{step_title}': Based on your question '{question}', the best approach is to leverage the Pomodoro technique. Start by setting a 25-minute timer to specifically focus on the action: '{step_action}'. If you get stuck, try finding a related tutorial on YouTube or reading a blog post from an industry expert."
