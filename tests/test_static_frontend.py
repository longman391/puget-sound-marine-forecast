"""Tests for safely serving the built frontend."""

from contextlib import asynccontextmanager

from fastapi.testclient import TestClient

from app import main


@asynccontextmanager
async def noop_lifespan(app):
    """Skip background startup work for frontend route tests."""
    yield


def _client_with_frontend(monkeypatch, frontend_dir):
    monkeypatch.setattr(main, "FRONTEND_DIR", frontend_dir)
    test_app = main.create_app()
    test_app.router.lifespan_context = noop_lifespan
    return TestClient(test_app)


def test_spa_serves_files_inside_frontend_dir(tmp_path, monkeypatch):
    frontend_dir = tmp_path / "frontend" / "dist"
    frontend_dir.mkdir(parents=True)
    (frontend_dir / "assets").mkdir()
    (frontend_dir / "index.html").write_text("index page", encoding="utf-8")
    (frontend_dir / "manifest.json").write_text('{"name":"app"}', encoding="utf-8")

    with _client_with_frontend(monkeypatch, frontend_dir) as client:
        response = client.get("/manifest.json")

    assert response.status_code == 200
    assert response.text == '{"name":"app"}'


def test_spa_rejects_encoded_dot_segment_traversal(tmp_path, monkeypatch):
    frontend_dir = tmp_path / "frontend" / "dist"
    frontend_dir.mkdir(parents=True)
    (frontend_dir / "assets").mkdir()
    (frontend_dir / "index.html").write_text("index page", encoding="utf-8")
    (tmp_path / "frontend" / "secret.txt").write_text("secret", encoding="utf-8")

    with _client_with_frontend(monkeypatch, frontend_dir) as client:
        response = client.get("/%2e%2e/secret.txt")

    assert response.status_code == 200
    assert response.text == "index page"


def test_spa_rejects_encoded_absolute_path(tmp_path, monkeypatch):
    frontend_dir = tmp_path / "frontend" / "dist"
    frontend_dir.mkdir(parents=True)
    (frontend_dir / "assets").mkdir()
    (frontend_dir / "index.html").write_text("index page", encoding="utf-8")
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret", encoding="utf-8")

    with _client_with_frontend(monkeypatch, frontend_dir) as client:
        response = client.get(f"/%2F{secret_file.as_posix().lstrip('/')}")

    assert response.status_code == 200
    assert response.text == "index page"
