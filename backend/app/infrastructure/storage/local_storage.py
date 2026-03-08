from __future__ import annotations
import shutil
from pathlib import Path
from app.core.config import settings


class LocalStorageService:
    def __init__(self, root: str = settings.storage_root):
        self.root = root

    def job_dir(self, job_id: int) -> str:
        path = Path(self.root) / f"job_{job_id}"
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    def asset_path(self, job_id: int, filename: str) -> str:
        return str(Path(self.job_dir(job_id)) / filename)

    def delete_job_files(self, job_id: int) -> None:
        path = Path(self.root) / f"job_{job_id}"
        if path.exists():
            shutil.rmtree(path)
