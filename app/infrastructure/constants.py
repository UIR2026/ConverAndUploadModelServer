import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = Path(os.getenv("MODELS_DIR", str(BASE_DIR / "storage" / "models")))
TMP_DIR = Path(os.getenv("TMP_DIR", str(BASE_DIR / "tmp")))
DATABASE_PATH = BASE_DIR / "db" / "app.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
API_KEY_HEADER_NAME = "X-API-Key"
API_KEYS = tuple(
    key.strip() for key in os.getenv("API_KEYS", "").split(",") if key.strip()
)
