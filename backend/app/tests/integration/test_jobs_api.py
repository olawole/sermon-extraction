import pytest
import pytest_asyncio
from unittest.mock import patch
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def mock_background_tasks():
    with patch("app.api.routes.jobs.run_job_pipeline"), \
         patch("app.api.routes.jobs.run_render_highlight"):
        yield


@pytest.mark.asyncio
async def test_create_job(client: AsyncClient):
    response = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert response.status_code == 201
    data = response.json()
    assert data["stage"] == "pending"
    assert "id" in data
    assert data["youtube_url"].startswith("https://www.youtube.com/")


@pytest.mark.asyncio
async def test_get_job(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert create_resp.status_code == 201
    job_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/jobs/{job_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == job_id


@pytest.mark.asyncio
async def test_get_job_not_found(client: AsyncClient):
    response = await client.get("/api/v1/jobs/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_jobs(client: AsyncClient):
    await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    response = await client.get("/api/v1/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_transcript(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/jobs/{job_id}/transcript")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "chunks" in data
    assert isinstance(data["chunks"], list)


@pytest.mark.asyncio
async def test_get_transcript_not_found(client: AsyncClient):
    response = await client.get("/api/v1/jobs/99999/transcript")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_segments(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/jobs/{job_id}/segments")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "section_segments" in data
    assert "service_segments" in data
    assert "sermon_segment" in data


@pytest.mark.asyncio
async def test_get_segments_not_found(client: AsyncClient):
    response = await client.get("/api/v1/jobs/99999/segments")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_highlights(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/jobs/{job_id}/highlights")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "highlights" in data
    assert isinstance(data["highlights"], list)


@pytest.mark.asyncio
async def test_get_highlights_not_found(client: AsyncClient):
    response = await client.get("/api/v1/jobs/99999/highlights")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_assets(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/jobs/{job_id}/assets")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "assets" in data
    assert isinstance(data["assets"], list)


@pytest.mark.asyncio
async def test_render_highlight_not_found(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    response = await client.post(f"/api/v1/jobs/{job_id}/highlights/99999/render")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_render_all_highlights(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    response = await client.post(f"/api/v1/jobs/{job_id}/render-all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_retry_job_not_found(client: AsyncClient):
    response = await client.post("/api/v1/jobs/99999/retry")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_retry_job_not_failed(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    # Job remains in pending state — retry should return 400
    response = await client.post(f"/api/v1/jobs/{job_id}/retry")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_retry_failed_job(client: AsyncClient):
    from app.domain.services.job_service import JobService
    from app.domain.enums.enums import JobStage
    from app.infrastructure.db.session import get_db

    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    # Manually set the job to failed via the API's own dependency override
    from app.main import app
    db_override = app.dependency_overrides.get(get_db)
    async for db in db_override():
        svc = JobService(db)
        await svc.update_stage(job_id, JobStage.failed, error="test failure")

    response = await client.post(f"/api/v1/jobs/{job_id}/retry")
    assert response.status_code == 200
    data = response.json()
    assert data["stage"] == "pending"
    assert data["error_message"] is None


@pytest.mark.asyncio
async def test_delete_job(client: AsyncClient):
    create_resp = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    job_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/jobs/{job_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/jobs/{job_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_job_not_found(client: AsyncClient):
    response = await client.delete("/api/v1/jobs/99999")
    assert response.status_code == 404

