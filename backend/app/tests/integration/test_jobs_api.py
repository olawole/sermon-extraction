import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_job(client: AsyncClient):
    response = await client.post("/api/v1/jobs/", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert response.status_code == 201
    data = response.json()
    assert data["stage"] == "pending"
    assert "id" in data
    assert "youtube.com" in data["youtube_url"]


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
