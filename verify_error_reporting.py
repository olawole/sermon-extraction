import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.workflows.orchestrators.job_orchestrator import JobOrchestrator
from app.domain.services.job_service import JobService
from app.domain.enums.enums import JobStage

DATABASE_URL = "sqlite+aiosqlite:///C:/Users/onidu/source/repos/sermon-extraction/backend/sermon_extraction.db"

async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        job_service = JobService(db)
        # Create a job
        job = await job_service.create_job("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        job_id = job.id
        print(f"Created job {job_id}")

        orchestrator = JobOrchestrator(db)
        # This should trigger the simulated failure
        await orchestrator.run_pipeline(job_id)

        # Refresh and check the job status
        await db.refresh(job)
        print(f"Job {job_id} stage: {job.stage}")
        print(f"Job {job_id} error_message:\n{job.error_message}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
