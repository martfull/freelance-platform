import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app

TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://testuser:testpassword@localhost:5432/testdb"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_register(client):
    r = client.post("/accounts/register", json={"email": "test@example.com", "password": "secret123"})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "test@example.com"
    assert data["system_role"] == "user"
    assert "id" in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "secret123"}
    client.post("/accounts/register", json=payload)
    r = client.post("/accounts/register", json=payload)
    assert r.status_code == 409


def test_register_short_password(client):
    r = client.post("/accounts/register", json={"email": "a@b.com", "password": "short"})
    assert r.status_code == 422


def test_login(client):
    client.post("/accounts/register", json={"email": "login@example.com", "password": "secret123"})
    r = client.post("/accounts/login", json={"email": "login@example.com", "password": "secret123"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/accounts/register", json={"email": "wp@example.com", "password": "secret123"})
    r = client.post("/accounts/login", json={"email": "wp@example.com", "password": "wrongpass"})
    assert r.status_code == 401


def test_me(client):
    client.post("/accounts/register", json={"email": "me@example.com", "password": "secret123"})
    login_r = client.post("/accounts/login", json={"email": "me@example.com", "password": "secret123"})
    token = login_r.json()["access_token"]
    r = client.get("/accounts/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "me@example.com"


def test_me_unauthorized(client):
    r = client.get("/accounts/me")
    assert r.status_code in (401, 403)


def test_refresh(client):
    client.post("/accounts/register", json={"email": "ref@example.com", "password": "secret123"})
    login_r = client.post("/accounts/login", json={"email": "ref@example.com", "password": "secret123"})
    refresh_token = login_r.json()["refresh_token"]
    r = client.post("/accounts/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_logout(client):
    client.post("/accounts/register", json={"email": "out@example.com", "password": "secret123"})
    login_r = client.post("/accounts/login", json={"email": "out@example.com", "password": "secret123"})
    tokens = login_r.json()
    r = client.post("/accounts/logout", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 204
    r2 = client.post("/accounts/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r2.status_code == 401
