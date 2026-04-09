from app.database.connection import Base ,get_db
from dotenv import load_dotenv
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from urllib.parse import urlparse, urlunparse

load_dotenv()
DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/fastapi_db")

def _normalize_test_db_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname == "db" and not os.path.exists("/.dockerenv"):
        netloc = parsed.netloc.replace("@db:", "@localhost:").replace("@db", "@localhost")
        return urlunparse(parsed._replace(netloc=netloc))
    return url

DATABASE_URL = _normalize_test_db_url(DATABASE_URL)

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def test_app_metadata_loaded():
    assert app.title == "My FastAPI App"
    