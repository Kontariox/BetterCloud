from fastapi import APIRouter, HTTPException, status, Depends
from backend.db.connect_db import get_db_connection
from backend.routes.auth.utils import get_current_user

router = APIRouter()

@router.delete("/{folder_id}")
def delete_folder(folder_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        row = cur.execute("SELECT id FROM folders WHERE id = ? AND owner_id = ?", (folder_id, current_user["id"]), ).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found or access denied",)

        cur.execute("UPDATE files SET folder_id = NULL, folder = '' WHERE folder_id = ?", (folder_id,))

        cur.execute("UPDATE folders SET parent_id = NULL WHERE parent_id = ?", (folder_id,))

        cur.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
        conn.commit()
        return {"deleted": True, "id": folder_id}
    finally:
        conn.close()