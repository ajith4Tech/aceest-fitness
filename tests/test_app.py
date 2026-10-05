import pytest
from app import app, members


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        members.clear()
        yield client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Welcome to ACEest Fitness & Gym"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_get_members_empty(client):
    response = client.get("/members")

    assert response.status_code == 200
    assert response.get_json() == []


def test_add_member(client):
    response = client.post(
        "/members",
        json={
            "name": "John",
            "age": 25
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 1
    assert data["name"] == "John"
    assert data["age"] == 25


def test_add_member_missing_data(client):
    response = client.post(
        "/members",
        json={
            "name": "John"
        }
    )

    assert response.status_code == 400


def test_bmi_calculation(client):
    response = client.post(
        "/bmi",
        json={
            "weight": 70,
            "height": 1.75
        }
    )

    assert response.status_code == 200
    assert response.get_json()["bmi"] == 22.86


def test_bmi_invalid_values(client):
    response = client.post(
        "/bmi",
        json={
            "weight": 0,
            "height": 1.75
        }
    )

    assert response.status_code == 400
