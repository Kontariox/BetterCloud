from fastapi import APIRouter, HTTPException, status, Depends
from backend.routes.auth.utils import get_db_connection, get_current_user

router = APIRouter()

@router.delete("/{note_id}")
def delete_note(note_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Verify ownership
        row = cur.execute("SELECT id FROM notes WHERE id = ? AND owner_id = ?",
                          (note_id, current_user["id"])).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")

        cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return {"status": "success", "message": "Note deleted"}
    finally:
        conn.close()