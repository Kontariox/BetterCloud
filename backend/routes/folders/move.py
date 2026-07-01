from fastapi import APIRouter, HTTPException, status, Depends
from backend.db.connect_db import get_db_connection
from backend.routes.auth.utils import get_current_user
from backend.routes.folders.schemas import MoveFolderRequest

router = APIRouter()

@router.post("/{folder_id}/move")
def move_folder(
        folder_id: int,
        req: MoveFolderRequest,
        current_user: dict = Depends(get_current_user),
):
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        folder = cur.execute("SELECT id, parent_id FROM folders WHERE id = ? AND owner_id = ?", (folder_id, current_user["id"]),).fetchone()
        if not folder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")

        if req.parent_id is not None:
            if req.parent_id == folder_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot move folder into itself")

            target = cur.execute("SELECT id FROM folders WHERE id = ? AND owner_id = ?", (req.parent_id, current_user["id"]),).fetchone()
            if not target:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target folder not found")

            curr_parent = req.parent_id
            while curr_parent is not None:
                row = cur.execute("SELECT parent_id FROM folders WHERE id = ?", (curr_parent,)).fetchone()
                if not row:
                    break
                curr_parent = row[0]
                if curr_parent == folder_id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot move a folder into one of its subfolders",)

        # Zmień parent_id w bazie danych
        cur.execute("UPDATE folders SET parent_id = ? WHERE id = ?", (req.parent_id, folder_id))
        conn.commit()
        return {"moved": True, "folder_id": folder_id, "parent_id": req.parent_id}
    finally:
        conn.close()