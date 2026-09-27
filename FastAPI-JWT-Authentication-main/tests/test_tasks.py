def test_task_crud(client, auth_headers):
    created = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Ship API", "description": "Finish the service"},
    )
    assert created.status_code == 201
    task = created.json()
    assert task["completed"] is False

    listed = client.get("/tasks", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/tasks/{task['id']}", headers=auth_headers)
    assert fetched.status_code == 200

    updated = client.put(
        f"/tasks/{task['id']}",
        headers=auth_headers,
        json={"completed": True, "title": "Ship the API"},
    )
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    deleted = client.delete(f"/tasks/{task['id']}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/tasks/{task['id']}", headers=auth_headers).status_code == 404


def test_users_can_only_access_their_own_tasks(client, auth_headers):
    created = client.post("/tasks", headers=auth_headers, json={"title": "Private task"})
    task_id = created.json()["id"]

    client.post("/register", json={"username": "bob", "password": "strong-password"})
    login = client.post("/login", json={"username": "bob", "password": "strong-password"})
    bob_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert client.get(f"/tasks/{task_id}", headers=bob_headers).status_code == 404
    assert client.put(f"/tasks/{task_id}", headers=bob_headers, json={"title": "Steal"}).status_code == 404
    assert client.delete(f"/tasks/{task_id}", headers=bob_headers).status_code == 404
    assert client.get("/tasks", headers=bob_headers).json() == []


def test_task_validation_and_invalid_id(client, auth_headers):
    invalid_task = client.post("/tasks", headers=auth_headers, json={"title": ""})
    assert invalid_task.status_code == 422

    missing_task = client.get("/tasks/999", headers=auth_headers)
    assert missing_task.status_code == 404

    invalid_id = client.get("/tasks/not-an-integer", headers=auth_headers)
    assert invalid_id.status_code == 422

    empty_update = client.put("/tasks/999", headers=auth_headers, json={})
    assert empty_update.status_code == 404
