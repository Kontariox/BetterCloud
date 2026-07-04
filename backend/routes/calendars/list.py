from fastapi import APIRouter, Depends
from backend.routes.auth.utils import get_db_connection, get_current_user

router = APIRouter()

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