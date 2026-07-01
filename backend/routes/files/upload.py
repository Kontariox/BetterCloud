from fastapi import APIRouter, UploadFile, File as FastAPIFile, HTTPException, status, Depends, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import hashlib
import secrets
from datetime import datetime, timezone
from backend.routes.auth.utils import get_current_user
from .config import UPLOAD_DIR
from backend.db.connect_db import get_db_connection
from .utils import get_or_create_folder

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file_route(
    file: UploadFile = FastAPIFile(...),
    folder: str = Form(''),
    # Poprawka: folder_id musi być Form(), nie query param — frontend wysyła go w FormData
    folder_id: int | None = Form(None),
    current_user: dict = Depends(get_current_user),
):
    # Streamowy zapis pliku (czytamy partiami, nie ładujemy całego pliku do pamięci)
    hasher = hashlib.sha256()
    size = 0
    ext = Path(file.filename or "").suffix
    stored_name = f"{secrets.token_hex(16)}{ext}"
    stored_path = UPLOAD_DIR / stored_name
    with open(stored_path, "wb") as out_f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            out_f.write(chunk)
            hasher.update(chunk)
            size += len(chunk)
    file_hash = hasher.hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    # Zapis metadanych do sqlite — zapisujemy też stored_name oraz folder_id
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # resolve folder_id: prefer explicit folder_id, otherwise create/find by name
        resolved_folder_id = None
        # Poprawka: użyj `is not None` zamiast truthy check (folder_id=0 jest falsy, ale poprawne)
        if folder_id is not None:
            # verify ownership
            row = cur.execute("SELECT id FROM folders WHERE id = ? AND owner_id = ?", (folder_id, current_user['id'])).fetchone()
            if not row:
                stored_path.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid folder_id")
            resolved_folder_id = folder_id
        elif folder:
            resolved_folder_id = get_or_create_folder(conn, current_user['id'], folder)

        cur.execute(
            "INSERT INTO files (owner_id, name, size, hash, created_at, stored_name, folder, folder_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (current_user["id"], file.filename, str(size), file_hash, now, stored_name, folder, resolved_folder_id)
        )
        conn.commit()
        file_id = cur.lastrowid
    finally:
        conn.close()

    return JSONResponse({
        "id": file_id,
        "original_name": file.filename,
        "stored_name": stored_name,
        "size": size,
        "hash": file_hash,
        "created_at": now,  # Poprawka: użyj tej samej wartości co w bazie
    }, status_code=status.HTTP_201_CREATED)