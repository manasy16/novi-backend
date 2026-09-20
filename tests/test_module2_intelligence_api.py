from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user, get_db
from app.main import app
from app.module2.repositories.intelligence_repository import (
    IntelligenceRepository,
)


def make_intelligence(student_id, discovery_run_id, marker):
    return SimpleNamespace(
        id=uuid4(),
        student_id=student_id,
        discovery_run_id=discovery_run_id,
        profile_summary={"marker": marker},
        insights=[{"marker": marker}],
        career_dna={"marker": marker},
        career_alignment={"marker": marker},
        skill_gaps=[{"marker": marker}],
        readiness={"marker": marker},
        created_at=datetime.now(timezone.utc),
    )


def request_as_user(user, snapshots, monkeypatch):
    app.dependency_overrides[get_db] = lambda: object()
    app.dependency_overrides[get_current_user] = lambda: user

    def get_latest(db, student_id):
        return snapshots.get(student_id)

    monkeypatch.setattr(
        IntelligenceRepository,
        "get_latest_intelligence",
        staticmethod(get_latest),
    )

    return TestClient(app)


def test_get_latest_student_intelligence(monkeypatch):
    student_id = uuid4()
    discovery_run_id = uuid4()
    snapshot = make_intelligence(student_id, discovery_run_id, "latest")
    user = SimpleNamespace(student_id=student_id)

    try:
        with request_as_user(
            user,
            {student_id: snapshot},
            monkeypatch,
        ) as client:
            response = client.get("/module2/intelligence")

        assert response.status_code == 200
        payload = response.json()
        assert payload["id"] == str(snapshot.id)
        assert payload["student_id"] == str(student_id)
        assert payload["discovery_run_id"] == str(discovery_run_id)
        assert payload["profile_summary"] == {"marker": "latest"}
        assert payload["insights"] == [{"marker": "latest"}]
        assert payload["career_dna"] == {"marker": "latest"}
        assert payload["career_alignment"] == {"marker": "latest"}
        assert payload["skill_gaps"] == [{"marker": "latest"}]
        assert payload["readiness"] == {"marker": "latest"}
    finally:
        app.dependency_overrides.clear()


def test_get_student_intelligence_returns_404_when_missing(monkeypatch):
    user = SimpleNamespace(student_id=uuid4())

    try:
        with request_as_user(user, {}, monkeypatch) as client:
            response = client.get("/module2/intelligence")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Student intelligence not found"
        }
    finally:
        app.dependency_overrides.clear()


def test_student_intelligence_isolated_to_authenticated_student(monkeypatch):
    student_a = uuid4()
    student_b = uuid4()
    snapshot_a = make_intelligence(student_a, uuid4(), "student-a")
    snapshot_b = make_intelligence(student_b, uuid4(), "student-b")
    user_a = SimpleNamespace(student_id=student_a)

    try:
        with request_as_user(
            user_a,
            {
                student_a: snapshot_a,
                student_b: snapshot_b,
            },
            monkeypatch,
        ) as client:
            response = client.get("/module2/intelligence")

        assert response.status_code == 200
        payload = response.json()
        assert payload["student_id"] == str(student_a)
        assert payload["profile_summary"] == {"marker": "student-a"}
        assert payload["profile_summary"] != {"marker": "student-b"}
    finally:
        app.dependency_overrides.clear()
