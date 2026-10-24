import json
import logging
from datetime import datetime
from typing import Optional

from anthropic import Anthropic
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User, Task, Subject, Activity, Block, Suggestion

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are StudyFlow, an AI study coach. You analyse a student's tasks, subjects,
activities, and schedule to give actionable, concise study suggestions.

Rules:
- Give 2 to 5 suggestions.
- Each suggestion has a "title" (short), "detail" (1-2 sentences), and
  "kind" which is one of: prioritise, schedule, wellbeing, technique.
- Respond ONLY with valid JSON, no markdown fences, in this exact format:

{"suggestions": [{"title": "...", "detail": "...", "kind": "prioritise"}, ...]}
"""


def _gather_context(db: Session, user: User) -> str:
    """Build a text summary of the user's study situation for Claude."""

    tasks = db.execute(
        select(Task).where(Task.user_id == user.id).order_by(Task.due_date)
    ).scalars().all()

    subjects = db.execute(
        select(Subject).where(Subject.user_id == user.id)
    ).scalars().all()

    activities = db.execute(
        select(Activity).where(Activity.user_id == user.id)
    ).scalars().all()

    upcoming_blocks = db.execute(
        select(Block)
        .where(Block.user_id == user.id, Block.start_time >= datetime.utcnow())
        .order_by(Block.start_time)
        .limit(20)
    ).scalars().all()

    lines = [
        f"Student: {user.name}",
        f"Timezone: {user.timezone}",
        f"Wake: {user.wake_time}  Sleep: {user.sleep_time}",
    ]

    # Subjects
    if subjects:
        lines.append("\nSubjects:")
        for s in subjects:
            lines.append(f"  - {s.name} (priority {s.priority}/5)")
    else:
        lines.append("\nNo subjects registered.")

    # Tasks
    if tasks:
        lines.append("\nTasks:")
        for t in tasks:
            due = t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else "no due date"
            lines.append(f"  - [{t.status}] {t.title} (est {t.est_minutes}m, due {due}, skips {t.skip_count})")
    else:
        lines.append("\nNo tasks.")

    # Activities
    if activities:
        lines.append("\nActivities:")
        for a in activities:
            lines.append(f"  - {a.name} (target {a.target_minutes_per_week}m/week)")
    else:
        lines.append("\nNo activities.")

    # Upcoming schedule
    if upcoming_blocks:
        lines.append("\nUpcoming schedule (next 20 blocks):")
        for b in upcoming_blocks:
            lines.append(f"  - {b.type} {b.start_time.strftime('%Y-%m-%d %H:%M')} → {b.end_time.strftime('%H:%M')}")
    else:
        lines.append("\nNo upcoming scheduled blocks.")

    return "\n".join(lines)


def _parse_suggestions(raw: str) -> list[dict]:
    """Extract suggestion dicts from Claude's response text."""
    try:
        data = json.loads(raw)
        return data.get("suggestions", [])
    except json.JSONDecodeError:
        # Try to find JSON within the response
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            try:
                data = json.loads(raw[start : end + 1])
                return data.get("suggestions", [])
            except json.JSONDecodeError:
                pass
        logger.warning("Could not parse AI response as JSON: %s", raw[:200])
        return []


def generate_suggestions(db: Session, user_id: int) -> list[Suggestion]:
    """
    Gather the user's study context, ask Claude for suggestions,
    persist them as Suggestion rows, and return them.
    """
    user = db.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured. Add it to .env")

    context = _gather_context(db, user)

    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context}],
    )

    raw_text = response.content[0].text
    parsed = _parse_suggestions(raw_text)

    saved: list[Suggestion] = []
    for item in parsed:
        kind = item.get("kind", "technique")
        suggestion = Suggestion(
            user_id=user_id,
            kind=kind,
            content=item,
        )
        db.add(suggestion)
        saved.append(suggestion)

    db.commit()
    for s in saved:
        db.refresh(s)

    return saved


def get_suggestions(db: Session, user_id: int) -> list[Suggestion]:
    """Return previously saved suggestions for a user, newest first."""
    result = db.execute(
        select(Suggestion)
        .where(Suggestion.user_id == user_id)
        .order_by(Suggestion.created_at.desc())
    )
    return list(result.scalars().all())
