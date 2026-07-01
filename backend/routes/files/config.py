from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "db" / "db.sqlite"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)