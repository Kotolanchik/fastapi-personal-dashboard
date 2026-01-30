def test_register_and_login(client):
    payload = {"email": "user@example.com", "password": "supersecret"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]

    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token


def test_auth_required(client):
    response = client.get("/health")
    assert response.status_code == 401
