# Portfolio Case Study: AI Goal Planner System

## 🚀 The Project
The **AI Goal Planner System** is a full-stack, production-grade AI platform that implements the famous "Brian Tracy 12-Step Goal Setting" methodology. It utilizes an orchestration of Predictive Machine Learning (Scikit-Learn) and Generative AI to provide users with a deeply structured, personalized action plan for their goals.

## 🧠 The Problem
Most AI applications are simple API wrappers. They take user text, send it to OpenAI, and return text. However, enterprise AI systems require **Data Validation, Predictive Preprocessing, Prompt Engineering Guardrails, and Robust Data Persistence**. 

The goal was to build a portfolio project that demonstrates Senior-Level AI Engineering, moving beyond scripts into an actual, deployable MLOps architecture.

## 🛠️ The Solution & Technology Stack
I designed an architecture that strictly enforces separation of concerns:

1. **Machine Learning Pipeline (Scikit-Learn & Pandas):**
   - Engineered numerical features (e.g., complexity indexing) from raw user strings.
   - Trained and persisted a `RandomForestClassifier` to estimate goal difficulty.
2. **LLM Prompt Engineering:**
   - Isolated prompt text into a version-controlled file system (`prompts/v1.txt`).
   - Implemented strict "Guardrails" demanding that the AI adhere exactly to a 12-step JSON schema, stripping away unwanted conversational markdown.
3. **FastAPI & Clean Architecture:**
   - Designed a robust REST API using Pydantic for validation and a decoupled Service Layer for business logic.
4. **Data Persistence (PostgreSQL & SQLAlchemy):**
   - Managed schema migrations with Alembic.
   - Utilized PostgreSQL's `JSONB` datatype for efficient storage of the AI's complex outputs.
5. **Testing & CI/CD Readiness (Pytest & Docker):**
   - Wrote comprehensive unit and integration tests.
   - Orchestrated the environment using `docker-compose.yml`, ensuring "it works on my machine" translates to "it works in production."

## 📈 Key Outcomes
- Successfully integrated classical ML with modern LLMs in a single transactional flow.
- Solved testing complexity by dynamically falling back to an in-memory SQLite database without sacrificing the native PostgreSQL `JSONB` features in production.
- Demonstrated end-to-end full-stack AI Engineering capabilities, proving readiness for complex, enterprise-scale AI roles.
