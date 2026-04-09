from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.auth.jwt_handler import JWTHandler
from app.database.connection import Base, get_db
from app.main import app
from app.models.user_model import User
from app.routes.note_routes import get_current_user
from app.service.note_service import NoteService


class _FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class _FakeDB:
    def __init__(self, user):
        self._user = user

    def query(self, model):
        if model is User:
            return _FakeQuery(self._user)
        return _FakeQuery(None)


@pytest.fixture(scope="function")
def client(monkeypatch):
    monkeypatch.setattr(Base.metadata, "create_all", lambda bind=None: None)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_dashboard_gets_user_notes(client: TestClient, monkeypatch):
    user_id = uuid4()
    fake_user = SimpleNamespace(id=user_id, name="Akash", email="akash@gmail.com")
    fake_db = _FakeDB(fake_user)
    notes = [SimpleNamespace(id=uuid4(), title="Task 1", content="hello", is_done=False)]

    called = {}

    def override_get_db():
        yield fake_db

    def fake_get_all(db, requested_user_id):
        called["db"] = db
        called["user_id"] = requested_user_id
        return notes

    monkeypatch.setattr(JWTHandler, "get_current_user_id", staticmethod(lambda request: user_id))
    monkeypatch.setattr(NoteService, "get_all", staticmethod(fake_get_all))
    app.dependency_overrides[get_db] = override_get_db

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert called["db"] is fake_db
    assert called["user_id"] == user_id


def test_create_note_redirects_to_dashboard(client: TestClient, monkeypatch):
    user_id = uuid4()
    fake_user = SimpleNamespace(id=user_id)
    fake_db = _FakeDB(fake_user)

    called = {}

    def override_get_db():
        yield fake_db

    def fake_create(db, data, requested_user_id):
        called["db"] = db
        called["title"] = data.title
        called["content"] = data.content
        called["user_id"] = requested_user_id

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(NoteService, "create", staticmethod(fake_create))

    response = client.post(
        "/notes/create",
        data={"title": "My Note", "content": "body"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers.get("location") == "/dashboard"
    assert called["db"] is fake_db
    assert called["title"] == "My Note"
    assert called["content"] == "body"
    assert called["user_id"] == user_id


def test_delete_note_redirects_to_dashboard(client: TestClient, monkeypatch):
    user_id = uuid4()
    note_id = uuid4()
    fake_user = SimpleNamespace(id=user_id)
    fake_db = _FakeDB(fake_user)

    called = {}

    def override_get_db():
        yield fake_db

    def fake_delete(db, requested_note_id, requested_user_id):
        called["db"] = db
        called["note_id"] = requested_note_id
        called["user_id"] = requested_user_id
        return {"message": "note deleted"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(NoteService, "delete", staticmethod(fake_delete))

    response = client.post(f"/notes/{note_id}/delete", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers.get("location") == "/dashboard"
    assert called["db"] is fake_db
    assert called["note_id"] == note_id
    assert called["user_id"] == user_id


def test_add_note():    
    login_response = client.post("/login", data={
        "email":"akashsoni@gmail.com",
        "password": "Admin@123"
    }, follow_redirects=False)

    note_add = client.post("/notes/create", data={
        "title":"nothing",
        "content":"nothing"
    })
    assert note_add.status_code == 200