from __future__ import annotations
import logging
from app.infrastructure.db.session import AsyncSessionLocal
from app.workflows.orchestrators.job_orchestrator import JobOrchestrator

logger = logging.getLogger(__name__)


async def run_job_pipeline(job_id: int) -> None:
    async with AsyncSessionLocal() as db:
        orchestrator = JobOrchestrator(db)
        await orchestrator.run_pipeline(job_id)


async def run_render_highlight(job_id: int, highlight_id: int) -> None:
    async with AsyncSessionLocal() as db:
        orchestrator = JobOrchestrator(db)
        await orchestrator.render_highlight(job_id, highlight_id)
