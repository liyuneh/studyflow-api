from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.db import get_db, init_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.routers import activities, ai, schedule, task


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    init_db()
    yield


app = FastAPI(
    title="StudyFlow API",
    description="A study task management API and Health Monitor",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS – allow the frontend to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(task.router, prefix="/tasks", tags=["tasks"])
app.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
app.include_router(activities.router, prefix="/activities", tags=["activities"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])


# ── Root / health ─────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Welcome to StudyFlow API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ── User CRUD ─────────────────────────────────────────────────────────
@app.get("/users", response_model=list[UserResponse])
def get_all_users(db: DBSession = Depends(get_db)):
    result = db.execute(select(User))
    return result.scalars().all()


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, db: DBSession = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DBSession = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: DBSession = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: DBSession = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
