from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TaskStatus = Literal["todo", "done", "skipped", "postponed"]
BlockType = Literal["study", "break", "activity", "sleep"]


# ── User ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=200)
    telegram_handle: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    timezone: str = "Africa/Nairobi"
    wake_time: str = "06:30"
    sleep_time: str = "22:30"


class UserResponse(UserCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ── Subject ───────────────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    priority: int = Field(default=3, ge=1, le=5)


class SubjectResponse(SubjectCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ── Task ──────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    subject_id: Optional[int] = None
    due_date: Optional[datetime] = None
    est_minutes: int = Field(default=60, gt=0, le=1440)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    subject_id: Optional[int] = None
    due_date: Optional[datetime] = None
    est_minutes: Optional[int] = Field(default=None, gt=0, le=1440)
    status: Optional[TaskStatus] = None


class TaskResponse(TaskCreate):
    id: int
    status: TaskStatus
    skip_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ── Activity ──────────────────────────────────────────────────────────

class ActivityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    goal: Optional[str] = Field(default=None, max_length=200)
    target_minutes_per_week: int = Field(default=120, gt=0)


class ActivityResponse(ActivityCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ── Block ─────────────────────────────────────────────────────────────

class BlockCreate(BaseModel):
    type: BlockType
    start_time: datetime
    end_time: datetime
    task_id: Optional[int] = None
    activity_id: Optional[int] = None


class BlockResponse(BlockCreate):
    id: int
    completed: bool
    model_config = ConfigDict(from_attributes=True)


# ── Suggestion ────────────────────────────────────────────────────────

class SuggestionResponse(BaseModel):
    id: int
    kind: str
    content: dict
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, min_length=1, max_length=200)
    telegram_handle: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    timezone: Optional[str] = None
    wake_time: Optional[str] = None
    sleep_time: Optional[str] = None
