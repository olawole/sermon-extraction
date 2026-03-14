from __future__ import annotations
import sys
import os
import asyncio
import time
from pathlib import Path

# Add backend to sys.path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.config import settings
from app.infrastructure.db.session import AsyncSessionLocal
from app.domain.services.job_service import JobService
from app.workflows.orchestrators.job_orchestrator import JobOrchestrator
from app.domain.enums.enums import JobStage

WHISPER_RATE = 0.006  # $0.006 per minute
GPT4O_MINI_INPUT_RATE = 0.15 / 1_000_000  # $0.15 per 1M tokens
GPT4O_MINI_OUTPUT_RATE = 0.60 / 1_000_000  # $0.60 per 1M tokens

async def run_benchmark(url: str):
    if not settings.openai_api_key or settings.openai_api_key == "sk-...":
        print("Error: OPENAI_API_KEY is not set.")
        return

    # Force OpenAI providers
    settings.transcription_provider = "openai"
    settings.classification_provider = "openai"

    async with AsyncSessionLocal() as db:
        job_service = JobService(db)
        job = await job_service.create_job(url)
        job_id = job.id
        await db.commit()

        orchestrator = JobOrchestrator(db)
        
        print(f"Starting benchmark for Job {job_id} with URL: {url}")
        print(f"Using Providers: transcription={settings.transcription_provider}, classification={settings.classification_provider}")
        
        start_total = time.time()
        
        last_stage = None
        stage_times = {}
        stage_start = start_total

        # Start the pipeline
        pipeline_task = asyncio.create_task(orchestrator.run_pipeline(job_id))
        
        while not pipeline_task.done():
            await asyncio.sleep(0.5)
            # Poll job status to track stages
            # Need a fresh session or refresh the job
            async with AsyncSessionLocal() as db_poll:
                js_poll = JobService(db_poll)
                current_job = await js_poll.get_job(job_id)
                if current_job and current_job.stage != last_stage:
                    now = time.time()
                    if last_stage:
                        stage_times[last_stage] = now - stage_start
                    
                    last_stage = current_job.stage
                    stage_start = now
                    print(f"[{now - start_total:6.2f}s] Stage: {last_stage.value}")

        # Finalize last stage
        now = time.time()
        if last_stage:
            stage_times[last_stage] = now - stage_start
        
        end_total = time.time()
        
        # Fetch final job state
        async with AsyncSessionLocal() as db_final:
            js_final = JobService(db_final)
            final_job = await js_final.get_job(job_id)
            duration_sec = final_job.duration_seconds or 0

        print("\n" + "="*40)
        print("BENCHMARK RESULTS")
        print("="*40)
        for stage, duration in stage_times.items():
            print(f"{stage.value:25}: {duration:7.2f}s")
        print("-" * 40)
        print(f"{'Total Pipeline Time':25}: {end_total - start_total:7.2f}s")
        print("="*40)

        # Cost estimation
        duration_min = duration_sec / 60
        whisper_cost = duration_min * WHISPER_RATE
        
        print(f"Media Duration: {duration_min:.2f} minutes")
        print(f"Estimated Whisper Cost: ${whisper_cost:.4f}")
        print(f"GPT-4o-mini Rate: ${GPT4O_MINI_INPUT_RATE*1e6:.2f}/1M input, ${GPT4O_MINI_OUTPUT_RATE*1e6:.2f}/1M output")
        print("NOTE: Real GPT cost requires token counting (not implemented in this script).")
        print("="*40)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=rtfVv7ZpXIs"
    asyncio.run(run_benchmark(url))
