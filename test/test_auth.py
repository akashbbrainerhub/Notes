import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.database.connection import Base
from app.main import app


@pytest.fixture(scope="function")
def client(monkeypatch):
    monkeypatch.setattr(Base.metadata, "create_all", lambda bind=None: None)
    with TestClient(app) as test_client:
        yield test_client


def test_register(client: TestClient):
    response = client.get("/register")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_login(client: TestClient):
    response = client.get("/login")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_root(client: TestClient):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers.get("location") == "/login"

# POST 

def test_register(client:TestClient):
    unique_email = f"raju_{uuid4().hex[:8]}@gmail.com"
    data={
        "name":"raju",
        "email": unique_email,
        "password":"password"
        }
    response = client.post("/register" , data=data, follow_redirects=False)
    print("\nStatus:", response.status_code)
    print("Headers:", response.headers)
    assert response.status_code == 302 
    assert response.headers["location"] == "/dashboard"
    
    
def test_login(client: TestClient):
    unique_email = f"raju_{uuid4().hex[:8]}@gmail.com"
    data = {
        "name": "raju",
        "email": unique_email,
        "password": "password"
    }

    register_response = client.post("/register", data=data, follow_redirects=False)
    assert register_response.status_code == 302
    login_response = client.post("/login", data={
        "email": unique_email,
        "password": "password"
    }, follow_redirects=False)

    print("\nStatus:", login_response.status_code)
    print("Headers:", login_response.headers)

    assert login_response.status_code == 302
    assert login_response.headers["location"] == "/dashboard"
