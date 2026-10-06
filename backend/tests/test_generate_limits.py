import os

os.environ.setdefault("GROQ_API_KEY", "test-key-not-used")  # generation is stubbed below
os.environ.setdefault("TRIPO_API_KEY", "test-key-not-used")

from fastapi.testclient import TestClient  # noqa: E402

import app.api.routes as routes  # noqa: E402
from app.core.rate_limit import SlidingWindowLimiter  # noqa: E402
from app.main import app  # noqa: E402


async def _stub(request, prompt, image_url, file):
    return {"status": "success", "message": "stubbed, no Tripo/Groq/Blender call"}


class _Busy:
    def locked(self):
        return True


def _client(monkeypatch, per_client=5, hourly=30):
    monkeypatch.setattr(routes, "_generate", _stub)
    monkeypatch.setattr(routes, "PER_CLIENT", SlidingWindowLimiter(limit=per_client, window_s=3600))
    monkeypatch.setattr(routes, "GLOBAL_HOURLY", SlidingWindowLimiter(limit=hourly, window_s=3600))
    return TestClient(app)


def _generate(client, ip):
    return client.post("/generate", data={"prompt": "a brass telescope"}, headers={"x-forwarded-for": ip})


def test_per_client_cap(monkeypatch):
    client = _client(monkeypatch, per_client=2)
    assert [_generate(client, "203.0.113.1").status_code for _ in range(3)] == [200, 200, 429]


def test_global_cap_holds_whatever_the_caller_claims(monkeypatch):
    client = _client(monkeypatch, per_client=100, hourly=2)
    assert [_generate(client, f"198.51.100.{i}").status_code for i in range(3)] == [200, 200, 429]


def test_busy_when_both_generation_slots_are_taken(monkeypatch):
    client = _client(monkeypatch)
    monkeypatch.setattr(routes, "GENERATION_SLOTS", _Busy())
    resp = _generate(client, "203.0.113.5")
    assert resp.status_code == 429
    assert "busy" in resp.json()["detail"]


def test_cors_only_admits_the_live_ui_and_local_dev(monkeypatch):
    client = _client(monkeypatch)
    preflight = {"Access-Control-Request-Method": "POST"}
    for origin in ("https://orbit-3d-pipeline.vercel.app", "http://localhost:3000"):
        resp = client.options("/generate", headers={"Origin": origin, **preflight})
        assert resp.headers.get("access-control-allow-origin") == origin
    evil = client.options("/generate", headers={"Origin": "https://evil.example", **preflight})
    assert "access-control-allow-origin" not in evil.headers
