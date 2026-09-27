from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.dependencies import CurrentUser, DbSession
from app.models import Task, User
from app.schemas import (
    LoginRequest,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.security import create_access_token, hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI JWT Authentication Microservice",
    description="A secure task API with SQLite persistence and JWT authentication.",
    version="1.0.0",
)


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "FastAPI JWT Authentication Microservice"}


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["authentication"])
def register(user_data: UserCreate, db: DbSession) -> User:
    existing_user = db.scalar(select(User).where(User.username == user_data.username))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already registered")

    user = User(username=user_data.username, hashed_password=hash_password(user_data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already registered") from exc
    db.refresh(user)
    return user


@app.post("/login", response_model=TokenResponse, tags=["authentication"])
def login(login_data: LoginRequest, db: DbSession) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == login_data.username))
    if user is None or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(str(user.id)))


def get_owned_task(task_id: int, current_user: User, db: Session) -> Task:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(task_data: TaskCreate, current_user: CurrentUser, db: DbSession) -> Task:
    task = Task(**task_data.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(current_user: CurrentUser, db: DbSession) -> list[Task]:
    return list(db.scalars(select(Task).where(Task.owner_id == current_user.id).order_by(Task.id)).all())


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def read_task(task_id: int, current_user: CurrentUser, db: DbSession) -> Task:
    return get_owned_task(task_id, current_user, db)


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: int, task_data: TaskUpdate, current_user: CurrentUser, db: DbSession) -> Task:
    task = get_owned_task(task_id, current_user, db)
    changes = task_data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one field is required")
    for field, value in changes.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int, current_user: CurrentUser, db: DbSession) -> None:
    task = get_owned_task(task_id, current_user, db)
    db.delete(task)
    db.commit()
