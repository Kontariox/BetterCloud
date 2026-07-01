from fastapi import APIRouter, Depends
from backend.routes.folders.schemas import CreateFolderRequest
from backend.db.connect_db import get_db_connection
from backend.routes.auth.utils import get_current_user
from datetime import datetime, timezone

router = APIRouter()

@router.post("/")
def create_folder(req: CreateFolderRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        existing = cur.execute("SELECT id FROM folders WHERE owner_id=? AND name=? AND (parent_id IS ? OR parent_id = ?)", (current_user["id"], req.name, req.parent_id, req.parent_id),).fetchone()
        if existing:
            return {"id": existing[0], "name": req.name}

        now = datetime.now(timezone.utc).isoformat()
        cur.execute("INSERT INTO folders (owner_id, name, parent_id, created_at) VALUES (?, ?, ?, ?)", (current_user["id"], req.name, req.parent_id, now),)
        conn.commit()
        return {"id": cur.lastrowid, "name": req.name}
    finally:
        conn.close()