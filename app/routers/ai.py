from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import SuggestionResponse
from app.services.ai_coach import generate_suggestions, get_suggestions

router = APIRouter()


@router.get("/suggestions", response_model=list[SuggestionResponse])
def list_suggestions(user_id: int = Query(...), db: Session = Depends(get_db)):
    """Return previously saved suggestions for a user."""
    return get_suggestions(db, user_id)


@router.post("/suggestions", response_model=list[SuggestionResponse], status_code=201)
def create_suggestions(user_id: int = Query(...), db: Session = Depends(get_db)):
    """Ask the AI coach to generate fresh suggestions for a user."""
    try:
        return generate_suggestions(db, user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
