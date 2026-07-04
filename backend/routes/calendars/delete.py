from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional, List
from backend.routes.auth.utils import get_db_connection, get_current_user

router = APIRouter()

@router.delete("/events/{event_id}")
def delete_event(event_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Verify ownership
        row = cur.execute("SELECT id FROM events WHERE id = ? AND owner_id = ?",
                          (event_id, current_user["id"])).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or access denied")

        cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        return {"status": "success", "message": "Event deleted"}
    finally:
        conn.close()