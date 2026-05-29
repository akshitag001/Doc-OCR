import io
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
import services.job_runner as job_runner


@pytest.fixture(autouse=True)
def disable_background_executor(monkeypatch):
    monkeypatch.setattr(job_runner._executor, "submit", lambda *args, **kwargs: None)
    yield


@pytest.mark.asyncio
async def test_process_rejects_invalid_type():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        file = io.BytesIO(b"bad data")
        response = await client.post("/api/documents/process", files={"file": ("test.txt", file, "text/plain")})
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_process_rejects_oversized_file():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        file = io.BytesIO(b"x" * (11 * 1024 * 1024))
        response = await client.post("/api/documents/process", files={"file": ("big.jpg", file, "image/jpeg")})
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_process_accepts_valid_jpeg():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        file = io.BytesIO(b"\xff\xd8\xff\xe0" + b"x" * 1024)
        response = await client.post("/api/documents/process", files={"file": ("test.jpg", file, "image/jpeg")})
        assert response.status_code == 202
        assert "job_id" in response.json()


@pytest.mark.asyncio
async def test_get_result_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/documents/nonexistent/result")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_result_pending():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        file = io.BytesIO(b"\xff\xd8\xff\xe0" + b"x" * 1024)
        post = await client.post("/api/documents/process", files={"file": ("pending.jpg", file, "image/jpeg")})
        job_id = post.json()["job_id"]
        get = await client.get(f"/api/documents/{job_id}/result")
        assert get.status_code == 200
        assert get.json()["status"] in ["pending", "processing", "completed"]


@pytest.mark.asyncio
async def test_list_documents_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_list_documents_after_upload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        file = io.BytesIO(b"\xff\xd8\xff\xe0" + b"x" * 1024)
        await client.post("/api/documents/process", files={"file": ("test2.jpg", file, "image/jpeg")})
        response = await client.get("/api/documents")
        assert response.status_code == 200
        assert len(response.json()) >= 1
