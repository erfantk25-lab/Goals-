import sys
import os
import random
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Ensure we can import from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app
from db.session import SessionLocal, engine
from db.models import DriftMetric, Alert, SystemLog, ModelMetric, LLMMetric, Base

# Create tables for simulation
Base.metadata.create_all(bind=engine)

client = TestClient(app)

NORMAL_GOALS = [
    "I want to learn Spanish.",
    "Run a 5k next month.",
    "Read 12 books this year.",
    "Save $5000 for a vacation.",
    "Learn to play the guitar."
]

DRIFT_GOALS = [
    "I want to fundamentally restructure the geopolitical landscape of eastern Europe by systematically analyzing macroeconomic trends, building an international consensus among key stakeholders, and leveraging advanced AI models to predict policy outcomes over the next three decades.",
    "My goal is to discover a new element in the periodic table by constructing a localized particle accelerator in my garage, sourcing rare earth metals from meteorites, and conducting highly classified quantum entanglement experiments while live-streaming to millions of followers.",
    "I intend to genetically engineer a new species of bioluminescent house plants that not only provide ambient lighting for eco-friendly homes but also actively purify the air of all known toxins, requiring zero water and surviving entirely on atmospheric nitrogen.",
]

def print_summary():
    db: Session = SessionLocal()
    print("\n" + "="*50)
    print("📊 MLOPS OBSERVABILITY SUMMARY 📊")
    print("="*50)
    
    print(f"Total API Logs: {db.query(SystemLog).count()}")
    print(f"Total Model Metrics: {db.query(ModelMetric).count()}")
    print(f"Total LLM Metrics: {db.query(LLMMetric).count()}")
    print(f"Total Drift Checks: {db.query(DriftMetric).count()}")
    
    alerts = db.query(Alert).all()
    print(f"\n🚨 TOTAL ALERTS FIRED: {len(alerts)}")
    for a in alerts[-5:]: # Show last 5
        print(f"  [{a.severity}] {a.alert_type}: {a.message}")
        
    db.close()

def run_simulation():
    print("🚀 Starting MLOps Monitoring Simulation...")
    
    # Phase 1: Normal Traffic
    print("\nPhase 1: Generating Normal Traffic (Building Baseline)...")
    for _ in range(40):
        goal = random.choice(NORMAL_GOALS)
        client.post("/api/v1/generate-goal-plan", json={
            "title": goal,
            "description": "Standard self improvement goal.",
            "category": "Personal"
        })
        print(".", end="", flush=True)
        
    # Phase 2: Drift Traffic
    print("\n\nPhase 2: Generating Drift Traffic (Triggering Anomalies)...")
    for _ in range(20):
        goal = random.choice(DRIFT_GOALS)
        client.post("/api/v1/generate-goal-plan", json={
            "title": goal,
            "description": goal * 2, # Make it extra long
            "category": "Science"
        })
        print("!", end="", flush=True)

    print("\n\n✅ Simulation Complete!")
    print_summary()

if __name__ == "__main__":
    run_simulation()
