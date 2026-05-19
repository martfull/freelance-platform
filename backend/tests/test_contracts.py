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


def _create_contract(client):
    client_token = _register_and_login(client, "client@contracts.com")
    freelancer_token = _register_and_login(client, "freelancer@contracts.com")

    task_id = client.post("/marketplace/tasks", json={
        "title": "Contract test task",
        "description": "Task for testing contract lifecycle flow",
        "budget_amount": "500.00",
    }, headers=auth(client_token)).json()["id"]

    offer_id = client.post(f"/marketplace/tasks/{task_id}/offers", json={
        "proposed_amount": "480.00",
    }, headers=auth(freelancer_token)).json()["id"]

    contract = client.post(f"/marketplace/offers/{offer_id}/accept", headers=auth(client_token)).json()
    return contract["id"], client_token, freelancer_token


def test_get_contract(client):
    contract_id, client_token, _ = _create_contract(client)
    r = client.get(f"/contracts/{contract_id}", headers=auth(client_token))
    assert r.status_code == 200
    assert r.json()["status"] == "pending_confirmation"


def test_non_participant_cannot_get_contract(client):
    contract_id, _, _ = _create_contract(client)
    outsider_token = _register_and_login(client, "outsider@contracts.com")
    r = client.get(f"/contracts/{contract_id}", headers=auth(outsider_token))
    assert r.status_code == 403


def test_confirm_by_client(client):
    contract_id, client_token, _ = _create_contract(client)
    r = client.post(f"/contracts/{contract_id}/confirm", headers=auth(client_token))
    assert r.status_code == 200
    data = r.json()
    assert data["client_confirmed_at"] is not None
    assert data["status"] == "pending_confirmation"


def test_confirm_by_both_activates_contract(client):
    contract_id, client_token, freelancer_token = _create_contract(client)
    client.post(f"/contracts/{contract_id}/confirm", headers=auth(client_token))
    r = client.post(f"/contracts/{contract_id}/confirm", headers=auth(freelancer_token))
    assert r.status_code == 200
    assert r.json()["status"] == "active"


def test_cancel_contract(client):
    contract_id, client_token, _ = _create_contract(client)
    r = client.post(f"/contracts/{contract_id}/cancel", headers=auth(client_token))
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"


def test_list_my_contracts(client):
    contract_id, client_token, _ = _create_contract(client)
    r = client.get("/contracts/my", headers=auth(client_token))
    assert r.status_code == 200
    ids = [c["id"] for c in r.json()]
    assert contract_id in ids
