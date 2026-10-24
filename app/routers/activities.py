from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Activity
from app.schemas import ActivityCreate, ActivityResponse

router = APIRouter()


@router.get("", response_model=list[ActivityResponse])
def list_activities(db: Session = Depends(get_db)):
    result = db.execute(select(Activity))
    return result.scalars().all()


@router.post("", response_model=ActivityResponse, status_code=201)
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db)):
    activity = Activity(**payload.model_dump(), user_id=1)  # TODO: replace with real auth user
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
