def register_and_login(client, email):
    payload = {"email": email, "password": "supersecret"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    response = client.post("/auth/login", json=payload)
    token = response.json()["access_token"]
    return token


def test_user_isolation(client):
    user1_token = register_and_login(client, "user1@example.com")
    user2_token = register_and_login(client, "user2@example.com")

    response = client.post(
        "/health",
        json={
            "sleep_hours": 7,
            "energy_level": 8,
            "wellbeing": 7,
        },
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert response.status_code == 200

    response = client.get(
        "/health",
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    assert response.status_code == 200
    assert response.json() == []
