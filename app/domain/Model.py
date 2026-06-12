from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Model:
    id: int | None
    version: str
    filename: str
    file_path: str
    created_at: datetime
    is_latest: bool