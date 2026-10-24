from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Block
from app.schemas import BlockCreate, BlockResponse

router = APIRouter()


@router.get("", response_model=list[BlockResponse])
def list_blocks(db: Session = Depends(get_db)):
    result = db.execute(select(Block))
    return result.scalars().all()


@router.post("", response_model=BlockResponse, status_code=201)
def create_block(payload: BlockCreate, db: Session = Depends(get_db)):
    block = Block(**payload.model_dump(), user_id=1)  # TODO: replace with real auth user
    db.add(block)
    db.commit()
    db.refresh(block)
    return block
