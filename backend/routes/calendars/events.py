from fastapi import APIRouter, Depends
from typing import Optional
from backend.routes.auth.utils import get_db_connection, get_current_user
from pydantic import BaseModel, field_validator
from datetime import datetime, timezone

router = APIRouter()

class CreateEventRequest(BaseModel):
    title: str
    description: Optional[str] = None
    date: str  # YYYY-MM-DD
    time: Optional[str] = None  # HH:MM

    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 255:
            raise ValueError("Title must be between 1 and 255 characters")
        return v

    @field_validator("date")
    @classmethod
    def date_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @field_validator("time")
    @classmethod
    def time_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip()
        if not v:
            return None
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        return v

@router.post("/events")
def create_event(req: CreateEventRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cur.execute(
            "INSERT INTO events (owner_id, title, description, date, time, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (current_user["id"], req.title, req.description, req.date, req.time, now)
        )
        conn.commit()
        return {
            "id": cur.lastrowid,
            "title": req.title,
            "description": req.description,
            "date": req.date,
            "time": req.time,
            "created_at": now
        }
    finally:
        conn.close()


@router.get("/events")
def list_events(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT id, title, description, date, time, created_at FROM events WHERE owner_id = ? ORDER BY date, time",
            (current_user["id"],)
        ).fetchall()

        events = []
        for r in rows:
            events.append({
                "id": r["id"],
                "title": r["title"],
                "description": r["description"],
                "date": r["date"],
                "time": r["time"],
                "created_at": r["created_at"]
            })
        return events
    finally:
        conn.close()