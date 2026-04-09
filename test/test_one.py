from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4
from app.database.connection import get_db, SessionLocal
from app.models.user_model import User
from sqlalchemy.orm import Session
from app.models.note_model import Note
from fastapi import Depends
client = TestClient(app)

def _register_test_user() -> str:
    unique_email = f"raju_{uuid4().hex[:8]}@gmail.com"
    response = client.post(
        "/register",
        data={
            "name": "raju",
            "email": unique_email,
            "password": "password"
        },
        follow_redirects=False
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/dashboard"
    return unique_email
    
def test_delete_note():
    unique_email = _register_test_user()
    title = f"delete_me_{uuid4().hex[:6]}"

    create_response = client.post(
        "/notes/create",
        data={"title": title, "content": "content for delete"},
        follow_redirects=False
    )
    assert create_response.status_code == 302
    assert create_response.headers["location"] == "/dashboard"

    with SessionLocal() as local_db:
        user = local_db.query(User).filter(User.email == unique_email).first()
        assert user is not None

        created_note = (
            local_db.query(Note)
            .filter(Note.user_id == user.id, Note.title == title)
            .first()
        )
        assert created_note is not None
        note_id = created_note.id

    delete_response = client.post(f"/notes/{note_id}/delete", follow_redirects=False)
    assert delete_response.status_code == 302
    assert delete_response.headers["location"] == "/dashboard"

    with SessionLocal() as local_db:
        deleted_note = local_db.query(Note).filter(Note.id == note_id).first()
        assert deleted_note is None


def test_get_all_notes():
    _register_test_user()
    note_one = f"note_one_{uuid4().hex[:6]}"
    note_two = f"note_two_{uuid4().hex[:6]}"

    first_create = client.post(
        "/notes/create",
        data={"title": note_one, "content": "first content"},
        follow_redirects=False
    )
    second_create = client.post(
        "/notes/create",
        data={"title": note_two, "content": "second content"},
        follow_redirects=False
    )
    assert first_create.status_code == 302
    assert second_create.status_code == 302

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert note_one in dashboard.text
    assert note_two in dashboard.text


def test_toggle_note():
    unique_email = _register_test_user()
    title = f"toggle_me_{uuid4().hex[:6]}"

    create_response = client.post(
        "/notes/create",
        data={"title": title, "content": "content for toggle"},
        follow_redirects=False
    )
    assert create_response.status_code == 302
    assert create_response.headers["location"] == "/dashboard"

    with SessionLocal() as local_db:
        user = local_db.query(User).filter(User.email == unique_email).first()
        assert user is not None

        created_note = (
            local_db.query(Note)
            .filter(Note.user_id == user.id, Note.title == title)
            .first()
        )
        assert created_note is not None
        note_id = created_note.id
        assert created_note.is_done is False

    toggle_response = client.post(f"/notes/{note_id}/toggle", follow_redirects=False)
    assert toggle_response.status_code == 302
    assert toggle_response.headers["location"] == "/dashboard"

    with SessionLocal() as local_db:
        toggled_note = local_db.query(Note).filter(Note.id == note_id).first()
        assert toggled_note is not None
        assert toggled_note.is_done is True
