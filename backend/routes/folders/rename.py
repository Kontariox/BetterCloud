from fastapi import APIRouter, HTTPException, status, Depends
from backend.db.connect_db import get_db_connection
from backend.routes.auth.utils import get_current_user
from backend.routes.folders.schemas import RenameFolderRequest

router = APIRouter()

@router.put("/{folder_id}/rename")
def rename_folder(
    folder_id: int,
    req: RenameFolderRequest,
    current_user: dict = Depends(get_current_user),
):
    """Zmienia nazwę folderu."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        row = cur.execute("SELECT id, owner_id FROM folders WHERE id = ?", (folder_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
        if row["owner_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        cur.execute("UPDATE folders SET name = ? WHERE id = ?", (req.name, folder_id))
        conn.commit()
        return {"success": True, "new_name": req.name}
    finally:
        conn.close()