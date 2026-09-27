# FastAPI JWT Authentication Microservice

A beginner-friendly, production-style REST API built with FastAPI, SQLAlchemy, SQLite, bcrypt password hashing, and JWT Bearer authentication.

## Features

- User registration and login
- Secure bcrypt password hashing
- JWT access tokens with configurable expiration
- Protected task CRUD endpoints
- Per-user task ownership isolation
- SQLite persistence through SQLAlchemy
- Automatic Swagger UI and ReDoc documentation
- Pytest coverage for authentication, validation, authorization, and CRUD
- Importable Postman collection

## Project Structure

```text
FastAPI JWT Authentication Microservice/
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- database.py
|   |-- dependencies.py
|   |-- main.py
|   |-- models.py
|   |-- schemas.py
|   `-- security.py
|-- postman/
|   `-- FastAPI-JWT-Authentication.postman_collection.json
|-- tests/
|   |-- conftest.py
|   |-- test_auth.py
|   `-- test_tasks.py
|-- .env.example
|-- .gitignore
|-- README.md
`-- requirements.txt
```

## Installation on Windows PowerShell

From the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks script activation, run the project with the virtual environment executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Edit `.env` and replace `JWT_SECRET_KEY` with a long, random value. The application uses SQLite by default and creates `app.db` automatically on startup.

## Run the Server

With the virtual environment activated:

```powershell
uvicorn app.main:app --reload
```

Without activating it:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

## API Endpoints

### Authentication

| Method | Path | Auth | Description | Success |
| --- | --- | --- | --- | --- |
| POST | `/register` | No | Create a user | `201 Created` |
| POST | `/login` | No | Validate credentials and issue a JWT | `200 OK` |

Registration and login JSON examples:

```json
{
  "username": "alice",
  "password": "strong-password"
}
```

### Tasks

All task endpoints require `Authorization: Bearer <access_token>` and only return or modify tasks owned by the authenticated user.

| Method | Path | Description | Success |
| --- | --- | --- | --- |
| POST | `/tasks` | Create a task | `201 Created` |
| GET | `/tasks` | List the current user's tasks | `200 OK` |
| GET | `/tasks/{task_id}` | Get one owned task | `200 OK` |
| PUT | `/tasks/{task_id}` | Update one or more fields | `200 OK` |
| DELETE | `/tasks/{task_id}` | Delete an owned task | `204 No Content` |

Common error responses include `401 Unauthorized` for missing or invalid credentials, `404 Not Found` for missing or non-owned tasks, `409 Conflict` for duplicate usernames, and `422 Unprocessable Entity` for invalid request data or IDs.

## API Documentation

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

In Swagger, register a user, log in, copy the returned `access_token`, click **Authorize**, enter `Bearer <token>`, and then call the task endpoints.

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The test suite uses an isolated in-memory SQLite database and does not modify the development database.

## Postman Usage

1. Start the API with Uvicorn.
2. Open Postman and select **Import**.
3. Choose `postman/FastAPI-JWT-Authentication.postman_collection.json`.
4. Run **Register** once.
5. Run **Login**. Its test script stores the JWT in the collection variable `token`.
6. Run **Create Task**, then **List Tasks**.
7. Set `task_id` to the returned task ID and run **Get Task**, **Update Task**, or **Delete Task**.

The collection uses `http://127.0.0.1:8000` as `base_url`; change that collection variable if the server runs elsewhere.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./app.db` | SQLAlchemy database URL |
| `JWT_SECRET_KEY` | Required | Secret used to sign JWTs |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime |
