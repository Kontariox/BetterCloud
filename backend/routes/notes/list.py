from fastapi import APIRouter, Depends
from backend.routes.auth.utils import get_db_connection, get_current_user

router = APIRouter()

@router.get("")
def list_notes(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE owner_id = ? ORDER BY updated_at DESC",
            (current_user["id"],)
        ).fetchall()

        notes = []
        for r in rows:
            notes.append({
                "id": r["id"],
                "title": r["title"],
                "content": r["content"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"]
            })
        return notes
    finally:
        conn.close()