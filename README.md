# 🎯 Goal Planner AI — MLOps & LLMOps Portfolio Project

> An end-to-end production-grade AI system that generates personalized 12-step goal plans using the **Brian Tracy methodology**, powered by **FastAPI**, **Streamlit**, **scikit-learn**, and **OpenAI GPT-4o**.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red?style=flat-square&logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.8-orange?style=flat-square&logo=scikit-learn)
![Docker](https://img.shields.io/badge/Docker-ready-blue?style=flat-square&logo=docker)

---

## ✨ Features

### 🤖 AI & LLM
- **Brian Tracy 12-Step Plans** — generates fully personalized goal plans using the proven Brian Tracy "Goals!" methodology
- **OpenAI GPT-4o Integration** — real AI generation when `OPENAI_API_KEY` is set; falls back to intelligent mock otherwise
- **RAG (Retrieval-Augmented Generation)** — toggle to enable live DuckDuckGo web search to ground plans with up-to-date information
- **A/B Prompt Testing** — randomly selects between `v1` (analytical) and `v2` (empathetic) prompts and tracks performance

### 📊 MLOps & LLMOps Dashboard
- **Real-time Metrics** — API latency, error rate, token usage, model accuracy
- **Live Time-Series Charts** — line charts for LLM latency and data drift over time
- **A/B Test Distribution** — bar chart showing which prompt version has been used most
- **Data Drift Detection** — monitors feature distribution shift with automated alerts
- **One-Click Model Retraining** — triggers Random Forest retraining as a background job

### 🎯 Goal Planning UX
- **8 Goal Templates** — one-click pre-fills for popular goals (marathon, SaaS, Python, etc.)
- **Interactive Progress Tracking** — checkboxes + live progress bar, persisted to database
- **Dynamic Replanning** — AI rewrites remaining steps when you fail one
- **Ask AI Chat** — ask the AI a question about any specific step
- **Export to Markdown** — download the full plan as a `.md` file
- **🏆 Completion Certificate** — confetti + downloadable certificate when all 12 steps done

---

## 🏗️ Architecture

```
goal-planner-ai/
├── api/                    # FastAPI backend
│   ├── endpoints/
│   │   ├── goals.py        # Goal generation, replan, ask-ai
│   │   └── metrics.py      # Dashboard metrics, retrain, history
│   ├── repositories/       # Repository pattern (DB access)
│   ├── schemas.py          # Pydantic request/response models
│   └── services.py         # Business logic layer
├── db/
│   ├── models.py           # SQLAlchemy ORM models
│   ├── migrations/         # Alembic migration scripts
│   └── session.py          # DB session factory
├── ml/
│   ├── llm_service.py      # OpenAI GPT-4o + A/B testing + RAG
│   ├── rag_service.py      # DuckDuckGo web search
│   ├── training/train.py   # Random Forest training pipeline
│   ├── evaluation/         # Model evaluation & metrics
│   └── registry/           # Model version registry
├── prompts/
│   ├── v1.txt              # Brian Tracy — analytical style
│   └── v2.txt              # Brian Tracy — empathetic style
├── frontend/
│   ├── app.py              # Streamlit UI
│   ├── api_client.py       # HTTP client for backend
│   └── style.css           # Premium dark theme CSS
├── tests/
│   └── test_integration.py # Integration test suite
├── Dockerfile              # Backend container
├── Dockerfile.frontend     # Frontend container
└── docker-compose.yml      # Orchestration
```

---

## 🚀 Quick Start

### Option 1: Local Development

**Prerequisites:** Python 3.11+

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/goal-planner-ai.git
cd goal-planner-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up the database
alembic upgrade head

# 4. (Optional) Set your OpenAI API key
export OPENAI_API_KEY=sk-...   # Linux/Mac
set OPENAI_API_KEY=sk-...      # Windows

# 5. Start the backend (Terminal 1)
uvicorn api.main:app --reload

# 6. Start the frontend (Terminal 2)
streamlit run frontend/app.py
```

Open **http://localhost:8501** in your browser.

### Option 2: Docker

```bash
# Build and start both services
docker-compose up --build

# With OpenAI API key
OPENAI_API_KEY=sk-... docker-compose up --build
```

---

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | No | — | Enables real GPT-4o generation. Falls back to mock if not set. |
| `DATABASE_URL` | No | `sqlite:///./goal_planner.db` | Database connection string |

---

## 🧪 Testing

```bash
pytest tests/test_integration.py -v
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI, Uvicorn |
| **Frontend** | Streamlit, streamlit-lottie |
| **ML Model** | scikit-learn Random Forest |
| **LLM** | OpenAI GPT-4o (with mock fallback) |
| **RAG** | DuckDuckGo Search API |
| **Database** | SQLite (Alembic migrations) |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic v2 |
| **Containers** | Docker, docker-compose |

---

## 📸 Screenshots

| Goal Planner | System Dashboard |
|---|---|
| *Generate AI plans with web search* | *Live MLOps metrics and charts* |

---

## 🗺️ Roadmap

- [ ] Real OpenAI API integration (requires API key)
- [ ] User authentication & multi-tenant support
- [ ] Google Calendar `.ics` export
- [ ] SMS/Email daily reminders (Twilio/SendGrid)
- [ ] Gamification (XP, levels, badges)

---

## 📄 License

MIT License — feel free to fork and build on this!

---

*Built as a portfolio project demonstrating MLOps, LLMOps, and Agentic AI engineering skills.*
