from fastapi import APIRouter, Depends
from backend.db.connect_db import get_db_connection
from backend.routes.auth.utils import get_current_user

router = APIRouter()

@router.get("/")
def list_folders(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        rows = cur.execute("SELECT id, name, parent_id, created_at FROM folders WHERE owner_id = ? ORDER BY name", (current_user["id"],),).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()