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


def _register_and_login(client, email, password="secret123"):
    client.post("/accounts/register", json={"email": email, "password": password})
    r = client.post("/accounts/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# --- Tasks ---

def test_list_tasks_empty(client):
    r = client.get("/marketplace/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_create_task(client):
    token = _register_and_login(client, "creator@test.com")
    r = client.post("/marketplace/tasks", json={
        "title": "Build a website",
        "description": "Need a full-stack developer for our project",
        "budget_amount": "500.00",
    }, headers=auth(token))
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Build a website"
    assert data["status"] == "open"


def test_create_task_unauthenticated(client):
    r = client.post("/marketplace/tasks", json={
        "title": "Build a website",
        "description": "Need a full-stack developer",
        "budget_amount": "500.00",
    })
    assert r.status_code in (401, 403)


def test_get_task(client):
    token = _register_and_login(client, "creator2@test.com")
    create_r = client.post("/marketplace/tasks", json={
        "title": "Design a logo",
        "description": "Creative logo for startup company",
        "budget_amount": "150.00",
    }, headers=auth(token))
    task_id = create_r.json()["id"]

    r = client.get(f"/marketplace/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["id"] == task_id


def test_update_task(client):
    token = _register_and_login(client, "owner@test.com")
    task_id = client.post("/marketplace/tasks", json={
        "title": "Write content",
        "description": "Need content writer for blog posts",
        "budget_amount": "200.00",
    }, headers=auth(token)).json()["id"]

    r = client.patch(f"/marketplace/tasks/{task_id}", json={"budget_amount": "250.00"}, headers=auth(token))
    assert r.status_code == 200
    assert r.json()["budget_amount"] == "250.00"


def test_cancel_task(client):
    token = _register_and_login(client, "canceler@test.com")
    task_id = client.post("/marketplace/tasks", json={
        "title": "Fix a bug",
        "description": "Need a developer to fix critical bug",
        "budget_amount": "100.00",
    }, headers=auth(token)).json()["id"]

    r = client.delete(f"/marketplace/tasks/{task_id}", headers=auth(token))
    assert r.status_code == 204


# --- Offers ---

def test_create_offer(client):
    client_token = _register_and_login(client, "client@test.com")
    freelancer_token = _register_and_login(client, "freelancer@test.com")

    task_id = client.post("/marketplace/tasks", json={
        "title": "Build API",
        "description": "Need Python developer for REST API project",
        "budget_amount": "800.00",
    }, headers=auth(client_token)).json()["id"]

    r = client.post(f"/marketplace/tasks/{task_id}/offers", json={
        "message": "I can do this!",
        "proposed_amount": "750.00",
    }, headers=auth(freelancer_token))
    assert r.status_code == 201
    assert r.json()["status"] == "pending"


def test_cannot_offer_own_task(client):
    token = _register_and_login(client, "selfbid@test.com")
    task_id = client.post("/marketplace/tasks", json={
        "title": "Self bid task",
        "description": "This task should not accept my own offer",
        "budget_amount": "300.00",
    }, headers=auth(token)).json()["id"]

    r = client.post(f"/marketplace/tasks/{task_id}/offers", json={}, headers=auth(token))
    assert r.status_code == 403


def test_duplicate_offer_rejected(client):
    client_token = _register_and_login(client, "client2@test.com")
    freelancer_token = _register_and_login(client, "freelancer2@test.com")

    task_id = client.post("/marketplace/tasks", json={
        "title": "Duplicate offer test",
        "description": "Testing duplicate offer prevention logic",
        "budget_amount": "400.00",
    }, headers=auth(client_token)).json()["id"]

    client.post(f"/marketplace/tasks/{task_id}/offers", json={}, headers=auth(freelancer_token))
    r = client.post(f"/marketplace/tasks/{task_id}/offers", json={}, headers=auth(freelancer_token))
    assert r.status_code == 409


def test_accept_offer_creates_contract(client):
    client_token = _register_and_login(client, "client3@test.com")
    freelancer_token = _register_and_login(client, "freelancer3@test.com")

    task_id = client.post("/marketplace/tasks", json={
        "title": "Full project",
        "description": "Complete web application development project",
        "budget_amount": "1000.00",
    }, headers=auth(client_token)).json()["id"]

    offer_id = client.post(f"/marketplace/tasks/{task_id}/offers", json={
        "proposed_amount": "950.00",
    }, headers=auth(freelancer_token)).json()["id"]

    r = client.post(f"/marketplace/offers/{offer_id}/accept", headers=auth(client_token))
    assert r.status_code == 201
    contract = r.json()
    assert contract["status"] == "pending_confirmation"
    assert contract["task_id"] == task_id


def test_withdraw_offer(client):
    client_token = _register_and_login(client, "client4@test.com")
    freelancer_token = _register_and_login(client, "freelancer4@test.com")

    task_id = client.post("/marketplace/tasks", json={
        "title": "Withdraw test task",
        "description": "Testing offer withdrawal functionality properly",
        "budget_amount": "300.00",
    }, headers=auth(client_token)).json()["id"]

    offer_id = client.post(f"/marketplace/tasks/{task_id}/offers", json={}, headers=auth(freelancer_token)).json()["id"]

    r = client.post(f"/marketplace/offers/{offer_id}/withdraw", headers=auth(freelancer_token))
    assert r.status_code == 204
