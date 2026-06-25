def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

def test_predict_goal(client):
    payload = {
        "title": "Learn Test Driven Development",
        "description": "I want to fully learn TDD and implement it in my daily Python workflow.",
        "category": "Career"
    }
    response = client.post("/api/v1/predict-goal", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "difficulty" in data
    assert "estimated_success_probability" in data
    assert data["estimated_completion_time_days"] > 0

def test_generate_goal_plan(client):
    payload = {
        "title": "Learn Test Driven Development",
        "description": "I want to fully learn TDD and implement it in my daily Python workflow.",
        "category": "Career"
    }
    response = client.post("/api/v1/generate-goal-plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "plan_data" in data
    assert "step_1" in data["plan_data"]
    assert "metadata" in data
    assert data["metadata"]["category"] == "Career"
    assert data["goal_id"] is not None

def test_get_history(client):
    # First generate a plan to ensure DB has data
    payload = {
        "title": "Another Goal",
        "description": "Another detailed description here.",
        "category": "Health"
    }
    client.post("/api/v1/generate-goal-plan", json=payload)
    
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Another Goal"
