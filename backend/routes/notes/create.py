from fastapi import APIRouter, Depends
from typing import Optional
from backend.routes.auth.utils import get_db_connection, get_current_user
from pydantic import BaseModel, field_validator
from datetime import datetime, timezone

router = APIRouter()

class CreateNoteRequest(BaseModel):
    title: Optional[str] = "Untitled Note"
    content: Optional[str] = ""

    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v: Optional[str]) -> str:
        if v is None:
            return "Untitled Note"
        v = v.strip()
        if len(v) > 255:
            raise ValueError("Title cannot exceed 255 characters")
        return v if v else "Untitled Note"

@router.post("/")
def create_note(req: CreateNoteRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cur.execute(
            "INSERT INTO notes (owner_id, title, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (current_user["id"], req.title, req.content, now, now)
        )
        conn.commit()
        return {
            "id": cur.lastrowid,
            "title": req.title,
            "content": req.content,
            "created_at": now,
            "updated_at": now
        }
    finally:
        conn.close()