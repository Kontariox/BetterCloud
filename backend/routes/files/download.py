from fastapi import APIRouter, HTTPException, status, Depends
from backend.routes.auth.utils import get_current_user
from .config import UPLOAD_DIR
from backend.db.connect_db import get_db_connection
from .utils import compute_hash
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/{file_id}")
def download_file(file_id: int, preview: bool = False, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        row = cur.execute("SELECT id, owner_id, name, size, hash, created_at, stored_name FROM files WHERE id = ?", (file_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono pliku.")
        # sprawdź, czy aktualny user jest właścicielem
        if row["owner_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu do pliku.")

        stored = row["stored_name"]
        upload_dir_resolved = UPLOAD_DIR.resolve()

        if stored:
            candidate = (UPLOAD_DIR / stored).resolve()
            # Bezpieczeństwo: ochrona przed path traversal
            if not candidate.is_relative_to(upload_dir_resolved):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nieprawidłowa ścieżka pliku.")
            if candidate.exists():
                found_path = candidate
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fizyczny plik nie istnieje na serwerze.")
        else:
            # fallback: spróbuj znaleźć po hash (stare wpisy przed migracją)
            target_hash = row["hash"]
            found_path = None
            for p in UPLOAD_DIR.iterdir():
                if p.is_file():
                    with open(p, "rb") as f:
                        if compute_hash(f.read()) == target_hash:
                            found_path = p
                            break
            if not found_path:
                # dodatkowy fallback po oryginalnej nazwie — z walidacją path traversal
                candidate = (UPLOAD_DIR / row["name"]).resolve()
                if candidate.is_relative_to(upload_dir_resolved) and candidate.exists():
                    found_path = candidate
            if not found_path:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fizyczny plik nie istnieje na serwerze.")
    finally:
        conn.close()

    return FileResponse(
        path=found_path,
        filename=row["name"] if not preview else None,
        content_disposition_type="inline" if preview else "attachment",
    )