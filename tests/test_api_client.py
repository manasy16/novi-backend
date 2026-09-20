import requests
import pytest

from frontend.api_client import (
    APIClient,
    APIClientError,
    AuthenticationError,
    BackendUnavailableError,
    IntelligenceNotFoundError,
)


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        return self.payload


def test_api_client_returns_student_intelligence(monkeypatch):
    response = FakeResponse(200, {"profile_summary": {"total_facts": 3}})
    calls = {}

    def fake_get(url, headers, timeout):
        calls.update({"url": url, "headers": headers, "timeout": timeout})
        return response

    monkeypatch.setattr("frontend.api_client.requests.get", fake_get)

    result = APIClient("http://localhost:8000/", "token").get_student_intelligence()

    assert result == {"profile_summary": {"total_facts": 3}}
    assert calls == {
        "url": "http://localhost:8000/module2/intelligence",
        "headers": {"Authorization": "Bearer token"},
        "timeout": 10,
    }


def test_api_client_distinguishes_auth_and_not_found(monkeypatch):
    client = APIClient("http://localhost:8000", "token")

    monkeypatch.setattr(
        "frontend.api_client.requests.get",
        lambda *args, **kwargs: FakeResponse(401, {"detail": "Expired token"}),
    )
    with pytest.raises(AuthenticationError, match="Expired token"):
        client.get_student_intelligence()

    monkeypatch.setattr(
        "frontend.api_client.requests.get",
        lambda *args, **kwargs: FakeResponse(
            404,
            {"detail": "Student intelligence not found"},
        ),
    )
    with pytest.raises(
        IntelligenceNotFoundError,
        match="Student intelligence not found",
    ):
        client.get_student_intelligence()


def test_api_client_distinguishes_backend_and_api_errors(monkeypatch):
    client = APIClient("http://localhost:8000", "token")

    def unavailable(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr("frontend.api_client.requests.get", unavailable)
    with pytest.raises(BackendUnavailableError, match="backend is unavailable"):
        client.get_student_intelligence()

    monkeypatch.setattr(
        "frontend.api_client.requests.get",
        lambda *args, **kwargs: FakeResponse(500, {"detail": "Server error"}),
    )
    with pytest.raises(APIClientError, match="Server error"):
        client.get_student_intelligence()
