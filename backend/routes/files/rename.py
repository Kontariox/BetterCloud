from fastapi import APIRouter, HTTPException, status, Depends
from backend.routes.auth.utils import get_current_user
from backend.db.connect_db import get_db_connection
from .schemas import RenameFileRequest

router = APIRouter()

@router.put("/{file_id}/rename")
def rename_file(file_id: int, req: RenameFileRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        row = cur.execute("SELECT id, owner_id FROM files WHERE id = ?", (file_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        if row['owner_id'] != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        cur.execute("UPDATE files SET name = ? WHERE id = ?", (req.name, file_id))
        conn.commit()
        return {"success": True, "new_name": req.name}
    finally:
        conn.close()