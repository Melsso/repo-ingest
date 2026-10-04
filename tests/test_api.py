from fastapi.testclient import TestClient

from repo_ingest.api import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_local_paths_refused(tmp_path):
    r = client.post("/ingest", json={"source": str(tmp_path)})
    assert r.status_code == 400


def test_disallowed_host():
    r = client.post("/ingest", json={"source": "https://evil.example/o/r"})
    assert r.status_code == 400
