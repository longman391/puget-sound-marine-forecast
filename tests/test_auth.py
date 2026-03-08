"""Tests for the API key auth dependency."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import require_api_key
from app.config import settings


def _make_app_with_auth():
    """Create a minimal app with an auth-protected endpoint."""
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(require_api_key)])
    async def protected():
        return {"ok": True}

    @app.get("/open")
    async def open_endpoint():
        return {"ok": True}

    return app


class TestAuthDisabled:
    def test_no_key_required_when_auth_disabled(self):
        original = settings.api_key
        settings.api_key = ""
        try:
            app = _make_app_with_auth()
            with TestClient(app) as client:
                resp = client.get("/protected")
                assert resp.status_code == 200
        finally:
            settings.api_key = original


class TestAuthEnabled:
    def setup_method(self):
        self._original = settings.api_key
        settings.api_key = "test-secret-key"

    def teardown_method(self):
        settings.api_key = self._original

    def test_valid_header_key(self):
        app = _make_app_with_auth()
        with TestClient(app) as client:
            resp = client.get("/protected", headers={"X-API-Key": "test-secret-key"})
            assert resp.status_code == 200

    def test_valid_query_key(self):
        app = _make_app_with_auth()
        with TestClient(app) as client:
            resp = client.get("/protected?api_key=test-secret-key")
            assert resp.status_code == 200

    def test_missing_key_returns_401(self):
        app = _make_app_with_auth()
        with TestClient(app) as client:
            resp = client.get("/protected")
            assert resp.status_code == 401

    def test_wrong_key_returns_401(self):
        app = _make_app_with_auth()
        with TestClient(app) as client:
            resp = client.get("/protected", headers={"X-API-Key": "wrong-key"})
            assert resp.status_code == 401
