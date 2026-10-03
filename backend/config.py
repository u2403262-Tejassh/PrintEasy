"""Environment-backed application settings."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    db_path: Path
    agent_key: str
    max_upload_mb: int = 25
    stale_claim_minutes: int = 10

    @classmethod
    def from_env(cls) -> "Settings":
        data_dir = Path(os.getenv("DATA_DIR", "data"))
        return cls(
            data_dir=data_dir,
            db_path=Path(os.getenv("DB_PATH", str(data_dir / "printeasy.sqlite3"))),
            agent_key=os.getenv("AGENT_KEY", ""),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "25")),
            stale_claim_minutes=int(os.getenv("STALE_CLAIM_MINUTES", "10")),
        )


settings = Settings.from_env()
