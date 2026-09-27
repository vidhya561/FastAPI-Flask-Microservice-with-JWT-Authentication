def test_register_and_login(client):
    registration = client.post("/register", json={"username": "alice", "password": "strong-password"})
    assert registration.status_code == 201
    assert registration.json()["username"] == "alice"
    assert "hashed_password" not in registration.json()

    login = client.post("/login", json={"username": "alice", "password": "strong-password"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]


def test_duplicate_and_invalid_login(client, registered_user):
    duplicate = client.post("/register", json=registered_user)
    assert duplicate.status_code == 409

    invalid = client.post("/login", json={"username": "alice", "password": "wrong-password"})
    assert invalid.status_code == 401
    assert "WWW-Authenticate" in invalid.headers


def test_validation_and_authentication(client):
    invalid_registration = client.post("/register", json={"username": "a", "password": "short"})
    assert invalid_registration.status_code == 422

    unauthenticated = client.get("/tasks")
    assert unauthenticated.status_code == 401

    invalid_token = client.get("/tasks", headers={"Authorization": "Bearer invalid"})
    assert invalid_token.status_code == 401
