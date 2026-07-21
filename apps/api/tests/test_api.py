import pytest
import uuid
from httpx import ASGITransport, AsyncClient

# Set test DB URL BEFORE importing app modules
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.db.session import Base, async_session, engine


@pytest.fixture(autouse=True)
async def reset_db():
    """Create fresh tables before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def unique():
    """Return a unique string for each test."""
    return str(uuid.uuid4())[:8]


# ============================================================
# HEALTH
# ============================================================
@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["api"] is True
    assert data["data"]["database"] is True
    assert "request_id" in data["meta"]


# ============================================================
# PROFILE CRUD
# ============================================================
@pytest.mark.asyncio
async def test_create_profile(client, unique):
    resp = await client.post("/api/v1/profiles", json={
        "name": f"Test {unique}",
        "slug": f"test-{unique}",
        "profile_type": "general",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["name"] == f"Test {unique}"
    assert data["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_list_profiles(client, unique):
    await client.post("/api/v1/profiles", json={"name": f"A-{unique}", "slug": f"a-{unique}"})
    await client.post("/api/v1/profiles", json={"name": f"B-{unique}", "slug": f"b-{unique}"})
    resp = await client.get("/api/v1/profiles")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["meta"]["total"] == 2


@pytest.mark.asyncio
async def test_get_profile_by_id(client, unique):
    create = await client.post("/api/v1/profiles", json={"name": f"G-{unique}", "slug": f"g-{unique}"})
    pid = create.json()["data"]["id"]
    resp = await client.get(f"/api/v1/profiles/{pid}")
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == f"G-{unique}"


@pytest.mark.asyncio
async def test_get_profile_not_found(client):
    resp = await client.get(f"/api/v1/profiles/{uuid.uuid4()}")
    assert resp.status_code == 404
    data = resp.json()
    assert data["success"] is False
    assert data["error"]["code"] == "PROFILE_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_profile(client, unique):
    create = await client.post("/api/v1/profiles", json={"name": f"Old-{unique}", "slug": f"old-{unique}"})
    pid = create.json()["data"]["id"]
    resp = await client.patch(f"/api/v1/profiles/{pid}", json={"name": f"New-{unique}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == f"New-{unique}"


@pytest.mark.asyncio
async def test_delete_profile(client, unique):
    create = await client.post("/api/v1/profiles", json={"name": f"Del-{unique}", "slug": f"del-{unique}"})
    pid = create.json()["data"]["id"]
    resp = await client.delete(f"/api/v1/profiles/{pid}")
    assert resp.status_code == 200
    assert resp.json()["data"]["deleted"] is True
    resp = await client.get(f"/api/v1/profiles/{pid}")
    assert resp.status_code == 404


# ============================================================
# PROFILE STATUS TRANSITIONS
# ============================================================
@pytest.mark.asyncio
async def test_profile_status_transitions(client, unique):
    create = await client.post("/api/v1/profiles", json={
        "name": f"T-{unique}", "slug": f"t-{unique}",
    })
    pid = create.json()["data"]["id"]
    resp = await client.post(f"/api/v1/profiles/{pid}/pause")
    assert resp.json()["data"]["status"] == "paused"
    resp = await client.post(f"/api/v1/profiles/{pid}/resume")
    assert resp.json()["data"]["status"] == "active"
    resp = await client.post(f"/api/v1/profiles/{pid}/archive")
    assert resp.json()["data"]["status"] == "archived"


# ============================================================
# SOURCE CRUD
# ============================================================
@pytest.mark.asyncio
async def test_source_crud(client, unique):
    p = await client.post("/api/v1/profiles", json={"name": f"Src-{unique}", "slug": f"src-{unique}"})
    pid = p.json()["data"]["id"]
    resp = await client.post("/api/v1/sources", json={
        "title": f"Video {unique}",
        "profile_id": pid,
        "source_type": "upload",
        "duration_ms": 30000,
    })
    assert resp.status_code == 201
    sid = resp.json()["data"]["id"]
    assert resp.json()["data"]["status"] == "new"
    resp = await client.get(f"/api/v1/sources/{sid}")
    assert resp.json()["data"]["title"] == f"Video {unique}"
    resp = await client.get("/api/v1/sources")
    assert resp.json()["meta"]["total"] >= 1
    resp = await client.patch(f"/api/v1/sources/{sid}", json={"status": "completed"})
    assert resp.json()["data"]["status"] == "completed"
    resp = await client.post(f"/api/v1/sources/{sid}/archive")
    assert resp.json()["data"]["status"] == "archived"


@pytest.mark.asyncio
async def test_source_not_found(client):
    resp = await client.get(f"/api/v1/sources/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "SOURCE_NOT_FOUND"


# ============================================================
# CANDIDATE APPROVAL AND REJECTION
# ============================================================
@pytest.mark.asyncio
async def test_candidate_approval_flow(client, unique):
    p = await client.post("/api/v1/profiles", json={"name": f"C-{unique}", "slug": f"c-{unique}"})
    pid = p.json()["data"]["id"]
    s = await client.post("/api/v1/sources", json={"title": f"Src-{unique}", "profile_id": pid})
    sid = s.json()["data"]["id"]
    c = await client.post("/api/v1/candidates", json={
        "source_id": sid, "profile_id": pid,
        "title": f"Cand-{unique}", "overall_score": 85.0,
    })
    cid = c.json()["data"]["id"]
    assert c.json()["data"]["approval_status"] == "pending"
    resp = await client.post(f"/api/v1/candidates/{cid}/approve")
    assert resp.json()["data"]["approval_status"] == "approved"
    resp = await client.post(f"/api/v1/candidates/{cid}/reject")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_candidate_reject(client, unique):
    p = await client.post("/api/v1/profiles", json={"name": f"CR-{unique}", "slug": f"cr-{unique}"})
    pid = p.json()["data"]["id"]
    s = await client.post("/api/v1/sources", json={"title": f"Src-{unique}", "profile_id": pid})
    sid = s.json()["data"]["id"]
    c = await client.post("/api/v1/candidates", json={"source_id": sid, "profile_id": pid, "title": f"Cand-{unique}"})
    cid = c.json()["data"]["id"]
    resp = await client.post(f"/api/v1/candidates/{cid}/reject")
    assert resp.json()["data"]["approval_status"] == "rejected"


@pytest.mark.asyncio
async def test_candidate_not_found(client):
    resp = await client.get(f"/api/v1/candidates/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "CANDIDATE_NOT_FOUND"


# ============================================================
# INVALID TRANSITIONS RETURN 409
# ============================================================
@pytest.mark.asyncio
async def test_invalid_candidate_transition_returns_409(client, unique):
    p = await client.post("/api/v1/profiles", json={"name": f"I-{unique}", "slug": f"i-{unique}"})
    pid = p.json()["data"]["id"]
    s = await client.post("/api/v1/sources", json={"title": f"Src-{unique}", "profile_id": pid})
    sid = s.json()["data"]["id"]
    c = await client.post("/api/v1/candidates", json={"source_id": sid, "profile_id": pid, "title": f"Cand-{unique}"})
    cid = c.json()["data"]["id"]
    await client.post(f"/api/v1/candidates/{cid}/archive")
    resp = await client.post(f"/api/v1/candidates/{cid}/approve")
    assert resp.status_code == 409


# ============================================================
# JOB CREATION AND STATUS TRANSITIONS
# ============================================================
@pytest.mark.asyncio
async def test_job_create_and_list(client):
    resp = await client.post("/api/v1/jobs", json={
        "job_type": "render_clip",
        "entity_type": "candidate",
        "entity_id": "test-entity",
        "priority": "high",
    })
    assert resp.status_code == 201
    assert resp.json()["data"]["status"] == "pending"
    resp = await client.get("/api/v1/jobs")
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_job_status_transitions(client):
    resp = await client.post("/api/v1/jobs", json={
        "job_type": "test", "entity_type": "candidate", "entity_id": "e1",
    })
    jid = resp.json()["data"]["id"]
    await client.post(f"/api/v1/jobs/{jid}/pause")
    resp = await client.get(f"/api/v1/jobs/{jid}")
    assert resp.json()["data"]["status"] == "paused"
    await client.post(f"/api/v1/jobs/{jid}/resume")
    resp = await client.get(f"/api/v1/jobs/{jid}")
    assert resp.json()["data"]["status"] == "queued"


@pytest.mark.asyncio
async def test_job_retry_restrictions(client):
    resp = await client.post("/api/v1/jobs", json={
        "job_type": "test", "entity_type": "candidate", "entity_id": "e2",
        "payload_json": {"test": True},
    })
    jid = resp.json()["data"]["id"]
    # Can retry a pending job (it's retryable by default)
    resp = await client.post(f"/api/v1/jobs/{jid}/retry")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_job_not_found(client):
    resp = await client.get(f"/api/v1/jobs/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_job_cancel(client):
    resp = await client.post("/api/v1/jobs", json={
        "job_type": "test", "entity_type": "candidate", "entity_id": "e-cancel",
    })
    jid = resp.json()["data"]["id"]
    resp = await client.post(f"/api/v1/jobs/{jid}/cancel")
    assert resp.json()["data"]["status"] == "cancelled"


# ============================================================
# SETTINGS
# ============================================================
@pytest.mark.asyncio
async def test_settings_retrieve_and_update(client):
    resp = await client.get("/api/v1/settings")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    resp = await client.patch("/api/v1/settings", json={"key": "max_parallel_jobs", "value": "8"})
    assert resp.status_code == 200
    assert resp.json()["data"]["value"] == "8"


# ============================================================
# NOTIFICATIONS
# ============================================================
@pytest.mark.asyncio
async def test_notification_read(client):
    resp = await client.get("/api/v1/notifications")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ============================================================
# PAGINATION RESPONSE FORMAT
# ============================================================
@pytest.mark.asyncio
async def test_pagination_format(client, unique):
    for i in range(5):
        await client.post("/api/v1/profiles", json={
            "name": f"P{i}-{unique}", "slug": f"p{i}-{unique}",
        })
    resp = await client.get("/api/v1/profiles?page=1&page_size=2")
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["meta"]["page"] == 1
    assert data["meta"]["page_size"] == 2
    assert data["meta"]["total"] == 5


# ============================================================
# STRUCTURED ERROR RESPONSE
# ============================================================
@pytest.mark.asyncio
async def test_structured_error_response(client):
    resp = await client.get(f"/api/v1/profiles/{uuid.uuid4()}")
    data = resp.json()
    assert data["success"] is False
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "details" in data["error"]
    assert "retryable" in data["error"]
    assert "request_id" in data["meta"]


@pytest.mark.asyncio
async def test_invalid_uuid_returns_422(client):
    resp = await client.get("/api/v1/profiles/not-a-uuid")
    assert resp.status_code == 422
    data = resp.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_job_create_with_payload(client):
    resp = await client.post("/api/v1/jobs", json={
        "job_type": "transcribe",
        "entity_type": "source",
        "entity_id": "e123",
        "payload_json": {"model": "large-v3", "language": "en"},
    })
    assert resp.status_code == 201
    assert resp.json()["data"]["job_type"] == "transcribe"
