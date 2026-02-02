from backend.app import models


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


def test_admin_role_required(client, db_session):
    payload = {"email": "admin@example.com", "password": "supersecret"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201

    admin_user = (
        db_session.query(models.User).filter(models.User.email == payload["email"]).first()
    )
    admin_user.role = "admin"
    db_session.commit()

    response = client.post("/auth/login", json=payload)
    token = response.json()["access_token"]

    response = client.get("/admin/users")
    assert response.status_code == 401

    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
