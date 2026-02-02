"""Smoke tests for main API endpoints: health, goals, analytics."""


def _auth_headers(client, email="smoke@example.com"):
    payload = {"email": email, "password": "supersecret"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/login", json=payload)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_smoke_health(client):
    headers = _auth_headers(client)
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_smoke_goals(client):
    headers = _auth_headers(client)
    response = client.get("/goals", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_smoke_analytics_correlations(client):
    headers = _auth_headers(client)
    response = client.get("/analytics/correlations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "correlations" in data


def test_smoke_analytics_insights(client):
    headers = _auth_headers(client)
    response = client.get("/analytics/insights", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
