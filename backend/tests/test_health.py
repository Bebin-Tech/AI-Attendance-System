from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import create_app


def test_live_does_not_require_database() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "aifams-api"}
    assert response.headers["X-Request-ID"]


def test_readiness_checks_dependencies() -> None:
    with patch(
        "app.main.check_dependencies", AsyncMock(return_value={"database": True, "redis": True})
    ):
        with TestClient(create_app()) as client:
            assert client.get("/api/v1/health/ready").status_code == 200


def test_readiness_fails_closed() -> None:
    with patch(
        "app.main.check_dependencies", AsyncMock(return_value={"database": False, "redis": True})
    ):
        with TestClient(create_app()) as client:
            response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["code"] == "DEPENDENCIES_UNAVAILABLE"
    assert "database_url" not in response.text


def test_unknown_routes_have_error_envelope() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/attendance/mark")
    assert response.status_code == 404
    assert set(response.json()) == {"code", "message", "details", "request_id"}
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
