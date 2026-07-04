from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from backend.routes.auth.utils import get_db_connection, get_current_user
from pydantic import BaseModel, field_validator
from datetime import datetime, timezone

router = APIRouter()

class UpdateNoteRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if len(v) > 255:
            raise ValueError("Title cannot exceed 255 characters")
        return v if v else "Untitled Note"

@router.put("/{note_id}")
def update_note(note_id: int, req: UpdateNoteRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Verify ownership
        row = cur.execute("SELECT id, title, content FROM notes WHERE id = ? AND owner_id = ?",
                          (note_id, current_user["id"])).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")

        now = datetime.now(timezone.utc).isoformat()

        # Determine values to update
        updated_title = req.title if req.title is not None else row["title"]
        updated_content = req.content if req.content is not None else row["content"]

        cur.execute(
            "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
            (updated_title, updated_content, now, note_id)
        )
        conn.commit()

        return {
            "id": note_id,
            "title": updated_title,
            "content": updated_content,
            "updated_at": now
        }
    finally:
        conn.close()