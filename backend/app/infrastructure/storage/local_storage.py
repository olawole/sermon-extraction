from __future__ import annotations
import os
import shutil
from app.core.config import settings


class LocalStorageService:
    def __init__(self, root: str = settings.storage_root):
        self.root = root

    def job_dir(self, job_id: int) -> str:
        path = os.path.join(self.root, f"job_{job_id}")
        os.makedirs(path, exist_ok=True)
        return path

    def asset_path(self, job_id: int, filename: str) -> str:
        return os.path.join(self.job_dir(job_id), filename)

    def delete_job_files(self, job_id: int) -> None:
        path = os.path.join(self.root, f"job_{job_id}")
        if os.path.exists(path):
            shutil.rmtree(path)
