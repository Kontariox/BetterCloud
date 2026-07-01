from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "db"
DB_PATH = BASE_DIR / "db" / "db.sqlite"